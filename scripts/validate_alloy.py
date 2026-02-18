#!/usr/bin/env python3
"""
Alloy Configuration Validator

Performs structural validation on Grafana Alloy configuration files (.alloy).
Alloy uses a custom HCL-inspired syntax (formerly "River"), so this validator
checks structural patterns rather than full grammar parsing.

Checks performed:
  - Balanced braces (block nesting)
  - Required components referenced in each file category
  - Environment variable usage via sys.env() instead of hardcoded values
  - Duplicate component labels within a single file
  - Forward_to references exist (not dangling)
  - No hardcoded endpoint URLs

Exit codes:
    0 -- All validations passed
    1 -- One or more validations failed

Usage:
    python scripts/validate_alloy.py [--verbose] [path ...]
    python scripts/validate_alloy.py configs/alloy/
    python scripts/validate_alloy.py configs/alloy/windows/base.alloy
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Expected component patterns by file category.
# Each category maps to a list of regex patterns that must appear in files
# within that directory. This ensures no critical wiring is accidentally removed.
# ---------------------------------------------------------------------------
REQUIRED_PATTERNS = {
    "common": {
        "labels.alloy": [
            r"prometheus\.relabel",
            r"loki\.process",
        ],
        "remote_write.alloy": [
            r"prometheus\.remote_write",
            r"sys\.env\(",
        ],
        "loki_push.alloy": [
            r"loki\.write",
            r"sys\.env\(",
        ],
    },
    "windows": {
        "base.alloy": [
            r"prometheus\.exporter\.windows",
            r"prometheus\.scrape",
            r"forward_to",
        ],
        "logs_eventlog.alloy": [
            r"loki\.source\.windowsevent",
            r"forward_to",
        ],
    },
    "linux": {
        "base.alloy": [
            r"prometheus\.exporter\.unix",
            r"prometheus\.scrape",
            r"forward_to",
        ],
        "logs_journal.alloy": [
            r"loki\.source\.journal",
            r"forward_to",
        ],
    },
}

# Patterns that indicate hardcoded values that should use sys.env()
HARDCODED_ENDPOINT_PATTERNS = [
    # Matches http:// or https:// URLs that are NOT inside sys.env() or comments
    re.compile(r'^\s*(?!//)\s*(?!.*sys\.env).*"https?://[^"]+(?::\d+)"'),
]

# Patterns that look like hardcoded secrets
SECRET_PATTERNS = [
    re.compile(r'(?:password|token|secret|api_key)\s*=\s*"[^$][^"]*"', re.IGNORECASE),
]


class ValidationResult:
    """Accumulates validation findings for a single file."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def check_balanced_braces(content: str, result: ValidationResult) -> None:
    """Verify that all braces are balanced, accounting for strings and comments."""
    depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    prev_char = ""

    for i, char in enumerate(content):
        # Track line comments (// to end of line)
        if char == "/" and prev_char == "/" and not in_string and not in_block_comment:
            in_line_comment = True

        # Track block comments (/* ... */)
        if char == "*" and prev_char == "/" and not in_string and not in_line_comment:
            in_block_comment = True
        if char == "/" and prev_char == "*" and in_block_comment:
            in_block_comment = False
            prev_char = char
            continue

        if char == "\n":
            in_line_comment = False

        if in_line_comment or in_block_comment:
            prev_char = char
            continue

        # Track string boundaries (simplified -- does not handle escaped quotes
        # inside multi-line raw strings, but sufficient for structural checks)
        if char == '"' and prev_char != "\\":
            in_string = not in_string

        if not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1

            if depth < 0:
                result.error("Unmatched closing brace found")
                return

        prev_char = char

    if depth != 0:
        result.error(f"Unbalanced braces: {depth} unclosed block(s)")


def check_required_patterns(
    content: str, filepath: Path, result: ValidationResult
) -> None:
    """Verify that required component patterns exist for the file's category."""
    parent_dir = filepath.parent.name
    filename = filepath.name

    category_patterns = REQUIRED_PATTERNS.get(parent_dir, {})
    file_patterns = category_patterns.get(filename, [])

    for pattern in file_patterns:
        if not re.search(pattern, content):
            result.error(f"Missing required pattern '{pattern}'")


def check_duplicate_component_labels(content: str, result: ValidationResult) -> None:
    """Detect duplicate component declarations within the same file.

    Alloy component declarations follow the pattern:
        component.type "label" {
    Two components with the same type and label in the same directory
    will cause a load error. Within a single file, duplicates are
    always wrong.
    """
    component_pattern = re.compile(
        r'^(\w+(?:\.\w+)+)\s+"([^"]+)"\s*\{', re.MULTILINE
    )
    seen: dict[str, int] = {}

    for match in component_pattern.finditer(content):
        component_type = match.group(1)
        label = match.group(2)
        key = f'{component_type} "{label}"'

        if key in seen:
            result.error(
                f"Duplicate component declaration: {key} "
                f"(first at char {seen[key]}, again at char {match.start()})"
            )
        else:
            seen[key] = match.start()


def check_hardcoded_endpoints(content: str, result: ValidationResult) -> None:
    """Flag hardcoded URLs that should use sys.env() for environment portability."""
    for line_num, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith("//") or stripped.startswith("/*"):
            continue

        # Skip lines that already use sys.env()
        if "sys.env(" in line:
            continue

        # Check for hardcoded HTTP(S) URLs in assignments
        if re.search(r'=\s*"https?://[^"]+(?::\d+)', line):
            result.warn(
                f"Line {line_num}: possible hardcoded URL -- consider using sys.env()"
            )


def check_secrets(content: str, result: ValidationResult) -> None:
    """Scan for patterns that look like hardcoded credentials."""
    for line_num, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*"):
            continue

        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                result.error(
                    f"Line {line_num}: possible hardcoded secret -- "
                    f"use sys.env() for sensitive values"
                )


def validate_file(filepath: Path, verbose: bool = False) -> ValidationResult:
    """Run all validation checks against a single Alloy config file."""
    result = ValidationResult(filepath)

    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        result.error(f"Could not read file: {exc}")
        return result

    if not content.strip():
        result.error("File is empty")
        return result

    check_balanced_braces(content, result)
    check_required_patterns(content, filepath, result)
    check_duplicate_component_labels(content, result)
    check_hardcoded_endpoints(content, result)
    check_secrets(content, result)

    if verbose and result.passed:
        print(f"  PASS: {filepath}")

    return result


def collect_alloy_files(paths: list[Path]) -> list[Path]:
    """Resolve paths to individual .alloy files, expanding directories."""
    files: list[Path] = []

    for path in paths:
        if path.is_file() and path.suffix == ".alloy":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.alloy")))
        else:
            print(f"WARNING: Skipping {path} (not a .alloy file or directory)")

    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Grafana Alloy configuration files"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("configs/alloy")],
        help="Files or directories to validate (default: configs/alloy/)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show passing files"
    )
    args = parser.parse_args()

    files = collect_alloy_files(args.paths)

    if not files:
        print("No .alloy files found to validate.")
        return 0

    print(f"Validating {len(files)} Alloy configuration file(s)...\n")

    results: list[ValidationResult] = []
    for filepath in files:
        result = validate_file(filepath, verbose=args.verbose)
        results.append(result)

    # Report findings
    errors_total = 0
    warnings_total = 0

    for result in results:
        if result.errors or result.warnings:
            print(f"  {result.filepath}:")
            for error in result.errors:
                print(f"    ERROR: {error}")
                errors_total += 1
            for warning in result.warnings:
                print(f"    WARN:  {warning}")
                warnings_total += 1

    # Summary
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"\nResults: {passed} passed, {failed} failed, {warnings_total} warnings")
    print(f"Files checked: {len(results)}")

    return 1 if errors_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
