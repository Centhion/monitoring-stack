#!/usr/bin/env python3
"""
Lightweight config validation hook.

Runs automatically via git hooks or editor integration. Performs fast syntax
checks only -- deep semantic validation is handled by validate_all.py.

Exit codes:
    0 -- Validation passed (or file type not applicable)
    1 -- Validation failed (syntax error found)

Usage:
    python3 scripts/validate_on_save.py <file_path>
"""

import json
import sys
from pathlib import Path


def validate_yaml(filepath: Path) -> tuple[bool, str]:
    """Validate YAML syntax without importing external dependencies.

    Falls back gracefully if PyYAML is not installed -- prints a warning
    but does not block the workflow. PyYAML is listed as a project
    dependency but may not be available in all environments.
    """
    try:
        import yaml
    except ImportError:
        return True, "PyYAML not installed -- skipping YAML validation"

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            yaml.safe_load(fh)
        return True, f"YAML syntax OK: {filepath.name}"
    except yaml.YAMLError as exc:
        return False, f"YAML syntax error in {filepath.name}: {exc}"


def validate_json(filepath: Path) -> tuple[bool, str]:
    """Validate JSON syntax using the standard library."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            json.load(fh)
        return True, f"JSON syntax OK: {filepath.name}"
    except json.JSONDecodeError as exc:
        return False, f"JSON syntax error in {filepath.name}: {exc}"


def check_no_hardcoded_secrets(filepath: Path) -> tuple[bool, str]:
    """Scan for common patterns that suggest hardcoded secrets.

    This is a fast heuristic check, not a comprehensive secret scanner.
    """
    secret_patterns = [
        "password:",
        "api_key:",
        "apiKey:",
        "secret_key:",
        "private_key:",
        "token:",
        "webhook_url: http",
    ]

    # Exclude .env.example since it intentionally contains placeholder values
    if filepath.name == ".env.example":
        return True, "Skipping secret check for .env.example"

    try:
        content = filepath.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return True, "Could not read file for secret scan -- skipping"

    findings = []
    for pattern in secret_patterns:
        if pattern in content:
            # Allow environment variable references (${VAR} or $VAR patterns)
            lines = content.splitlines()
            for line_num, line in enumerate(lines, start=1):
                if pattern in line and "${" not in line and "$(" not in line:
                    # Skip comment lines
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith("//"):
                        continue
                    findings.append(
                        f"  Line {line_num}: possible hardcoded value matching '{pattern}'"
                    )

    if findings:
        detail = "\n".join(findings)
        return False, f"Potential hardcoded secrets in {filepath.name}:\n{detail}"

    return True, "No hardcoded secrets detected"


def determine_file_type(filepath: Path) -> str | None:
    """Map file path to a validation category based on location and extension.

    Returns None if the file does not need validation (e.g., markdown, Python).
    """
    suffix = filepath.suffix.lower()
    parts = filepath.parts

    # Grafana dashboard JSON files
    if "dashboards" in parts and suffix == ".json":
        return "json"

    # Grafana alert policy JSON files
    if "alerts" in parts and suffix == ".json":
        return "json"

    # Any JSON file in configs/
    if "configs" in parts and suffix == ".json":
        return "json"

    # YAML configs for Prometheus, Loki, Alertmanager, Grafana provisioning
    if "configs" in parts and suffix in (".yml", ".yaml"):
        return "yaml"

    # Prometheus alert rules
    if "alerts" in parts and suffix in (".yml", ".yaml"):
        return "yaml"

    # Alloy uses River syntax (.alloy or .river) -- no validator yet,
    # but still check for hardcoded secrets
    if "alloy" in parts:
        return "alloy"

    return None


def main() -> int:
    """Entry point. Validates the file passed as the first argument."""
    if len(sys.argv) < 2:
        print("Usage: validate_on_save.py <file_path>")
        return 0

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        return 0

    file_type = determine_file_type(filepath)
    if file_type is None:
        return 0

    all_passed = True

    # Syntax validation based on file type
    if file_type == "yaml":
        passed, message = validate_yaml(filepath)
        print(message)
        if not passed:
            all_passed = False

    elif file_type == "json":
        passed, message = validate_json(filepath)
        print(message)
        if not passed:
            all_passed = False

    # Secret scan applies to all config file types
    passed, message = check_no_hardcoded_secrets(filepath)
    print(message)
    if not passed:
        all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
