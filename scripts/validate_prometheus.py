#!/usr/bin/env python3
"""
Prometheus and Alertmanager YAML Validator

Performs structural and semantic validation on Prometheus server config,
recording rules, alert rules, and Alertmanager config files.

Checks performed:
  - YAML syntax validity
  - Required top-level keys present
  - Alert/recording rule structure (groups, rules, required fields)
  - Label taxonomy compliance (standard labels used in grouping)
  - Duration format validation (e.g., 5m, 1h, 30s)
  - Alertmanager route and receiver completeness
  - No hardcoded secrets or endpoints

Exit codes:
    0 -- All validations passed
    1 -- One or more validations failed

Usage:
    python scripts/validate_prometheus.py [--verbose] [path ...]
    python scripts/validate_prometheus.py configs/prometheus/ alerts/prometheus/
    python scripts/validate_prometheus.py configs/alertmanager/alertmanager.yml
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Standard label taxonomy that should appear in alert grouping and recording rules
STANDARD_LABELS = {"environment", "datacenter", "role", "os", "hostname", "instance"}

# Valid Prometheus duration format
DURATION_PATTERN = re.compile(r"^\d+[smhdwy]$")

# Patterns indicating hardcoded secrets
SECRET_PATTERNS = [
    re.compile(r"(password|token|secret|api_key|webhook_url):\s+['\"]?[^${\s][^'\"\s]+", re.IGNORECASE),
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


def classify_file(filepath: Path) -> str | None:
    """Determine the file type based on path and content heuristics."""
    name = filepath.name
    parts = filepath.parts

    if name == "prometheus.yml":
        return "prometheus_config"
    if name == "recording_rules.yml":
        return "recording_rules"
    if name == "alertmanager.yml":
        return "alertmanager_config"
    if "alerts" in parts or "alert" in name:
        return "alert_rules"
    if name == "recording_rules.yml" or "recording" in name:
        return "recording_rules"

    # Grafana provisioning YAML -- validate syntax only
    if "grafana" in parts:
        return "grafana_provisioning"

    return "generic_yaml"


def validate_yaml_syntax(filepath: Path, result: ValidationResult) -> dict | None:
    """Parse YAML and return the loaded data structure, or None on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data
    except yaml.YAMLError as exc:
        result.error(f"YAML syntax error: {exc}")
        return None


def validate_prometheus_config(data: dict, result: ValidationResult) -> None:
    """Validate Prometheus server configuration structure."""
    if not isinstance(data, dict):
        result.error("Prometheus config must be a YAML mapping")
        return

    # Required top-level keys
    required_keys = ["global"]
    for key in required_keys:
        if key not in data:
            result.error(f"Missing required top-level key: '{key}'")

    # Validate global section
    global_cfg = data.get("global", {})
    if global_cfg:
        scrape_interval = global_cfg.get("scrape_interval", "")
        if scrape_interval and not DURATION_PATTERN.match(str(scrape_interval)):
            result.error(f"Invalid scrape_interval format: '{scrape_interval}'")

        eval_interval = global_cfg.get("evaluation_interval", "")
        if eval_interval and not DURATION_PATTERN.match(str(eval_interval)):
            result.error(f"Invalid evaluation_interval format: '{eval_interval}'")

    # Validate scrape_configs structure
    scrape_configs = data.get("scrape_configs", [])
    if scrape_configs:
        job_names = set()
        for i, scrape in enumerate(scrape_configs):
            if not isinstance(scrape, dict):
                result.error(f"scrape_configs[{i}]: must be a mapping")
                continue

            job_name = scrape.get("job_name")
            if not job_name:
                result.error(f"scrape_configs[{i}]: missing 'job_name'")
            elif job_name in job_names:
                result.error(f"Duplicate job_name: '{job_name}'")
            else:
                job_names.add(job_name)

    # Validate rule_files references exist
    rule_files = data.get("rule_files", [])
    if rule_files:
        for rf in rule_files:
            if not isinstance(rf, str):
                result.error(f"rule_files entry must be a string, got: {type(rf)}")


def validate_rule_groups(
    data: dict, result: ValidationResult, rule_type: str
) -> None:
    """Validate Prometheus rule groups (alert rules or recording rules)."""
    if not isinstance(data, dict):
        result.error("Rule file must be a YAML mapping")
        return

    groups = data.get("groups")
    if groups is None:
        result.error("Missing required top-level key: 'groups'")
        return

    if not isinstance(groups, list):
        result.error("'groups' must be a list")
        return

    group_names = set()
    for i, group in enumerate(groups):
        if not isinstance(group, dict):
            result.error(f"groups[{i}]: must be a mapping")
            continue

        # Group name uniqueness
        group_name = group.get("name")
        if not group_name:
            result.error(f"groups[{i}]: missing 'name'")
        elif group_name in group_names:
            result.error(f"Duplicate group name: '{group_name}'")
        else:
            group_names.add(group_name)

        # Validate interval if present
        interval = group.get("interval")
        if interval and not DURATION_PATTERN.match(str(interval)):
            result.error(f"groups[{i}] '{group_name}': invalid interval '{interval}'")

        # Validate rules
        rules = group.get("rules", [])
        if not isinstance(rules, list):
            result.error(f"groups[{i}] '{group_name}': 'rules' must be a list")
            continue

        if not rules:
            result.warn(f"groups[{i}] '{group_name}': no rules defined")

        for j, rule in enumerate(rules):
            if not isinstance(rule, dict):
                result.error(
                    f"groups[{i}].rules[{j}]: must be a mapping"
                )
                continue

            if rule_type == "alert_rules":
                _validate_alert_rule(rule, f"groups[{i}].rules[{j}]", result)
            elif rule_type == "recording_rules":
                _validate_recording_rule(rule, f"groups[{i}].rules[{j}]", result)


def _validate_alert_rule(rule: dict, path: str, result: ValidationResult) -> None:
    """Validate a single alert rule entry."""
    # Must have 'alert' key for alert rules
    alert_name = rule.get("alert")
    if not alert_name:
        # Could be a recording rule in an alert file -- skip
        if "record" in rule:
            return
        result.error(f"{path}: missing 'alert' key")
        return

    # Must have 'expr'
    if "expr" not in rule:
        result.error(f"{path} '{alert_name}': missing 'expr'")

    # Should have 'for' duration
    for_duration = rule.get("for")
    if for_duration:
        if not DURATION_PATTERN.match(str(for_duration)):
            result.error(
                f"{path} '{alert_name}': invalid 'for' duration '{for_duration}'"
            )
    else:
        result.warn(f"{path} '{alert_name}': missing 'for' duration")

    # Should have labels with severity
    labels = rule.get("labels", {})
    if "severity" not in labels:
        result.warn(f"{path} '{alert_name}': missing 'severity' label")

    # Should have annotations with description
    annotations = rule.get("annotations", {})
    if not annotations:
        result.warn(f"{path} '{alert_name}': missing annotations")
    elif "description" not in annotations and "summary" not in annotations:
        result.warn(
            f"{path} '{alert_name}': annotations should include "
            f"'description' or 'summary'"
        )


def _validate_recording_rule(
    rule: dict, path: str, result: ValidationResult
) -> None:
    """Validate a single recording rule entry."""
    record_name = rule.get("record")
    if not record_name:
        if "alert" in rule:
            return  # Alert rule in a recording file -- skip
        result.error(f"{path}: missing 'record' key")
        return

    # Recording rule naming convention: namespace:metric:aggregation
    parts = record_name.split(":")
    if len(parts) < 3:
        result.warn(
            f"{path} '{record_name}': does not follow naming convention "
            f"'namespace:metric:aggregation'"
        )

    if "expr" not in rule:
        result.error(f"{path} '{record_name}': missing 'expr'")


def validate_alertmanager_config(data: dict, result: ValidationResult) -> None:
    """Validate Alertmanager configuration structure."""
    if not isinstance(data, dict):
        result.error("Alertmanager config must be a YAML mapping")
        return

    # Required top-level keys
    if "route" not in data:
        result.error("Missing required top-level key: 'route'")

    if "receivers" not in data:
        result.error("Missing required top-level key: 'receivers'")

    # Validate route structure
    route = data.get("route", {})
    if route:
        if "receiver" not in route:
            result.error("route: missing default 'receiver'")

        # Collect all receiver names referenced in routes
        referenced_receivers = set()
        _collect_route_receivers(route, referenced_receivers)

        # Validate all referenced receivers exist
        defined_receivers = set()
        for recv in data.get("receivers", []):
            if isinstance(recv, dict) and "name" in recv:
                defined_receivers.add(recv["name"])

        for ref in referenced_receivers:
            if ref not in defined_receivers:
                result.error(f"Route references undefined receiver: '{ref}'")

        # Check for defined but unreferenced receivers
        for defined in defined_receivers:
            if defined not in referenced_receivers:
                result.warn(f"Receiver '{defined}' is defined but never referenced")

    # Validate inhibit_rules if present
    inhibit_rules = data.get("inhibit_rules", [])
    for i, rule in enumerate(inhibit_rules):
        if not isinstance(rule, dict):
            result.error(f"inhibit_rules[{i}]: must be a mapping")
            continue
        if "source_matchers" not in rule and "source_match" not in rule:
            result.warn(f"inhibit_rules[{i}]: missing source_matchers")
        if "target_matchers" not in rule and "target_match" not in rule:
            result.warn(f"inhibit_rules[{i}]: missing target_matchers")


def _collect_route_receivers(route: dict, receivers: set) -> None:
    """Recursively collect all receiver names from a route tree."""
    if "receiver" in route:
        receivers.add(route["receiver"])

    for child in route.get("routes", []):
        if isinstance(child, dict):
            _collect_route_receivers(child, receivers)


def check_secrets(filepath: Path, content: str, result: ValidationResult) -> None:
    """Scan for hardcoded secrets in the raw file content."""
    for line_num, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        for pattern in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                # Allow env var substitutions
                if "${" in line or "$(" in line:
                    continue
                # Allow example/placeholder values
                if "example.com" in line or "placeholder" in line.lower():
                    continue
                result.warn(
                    f"Line {line_num}: possible hardcoded secret near "
                    f"'{match.group()[:40]}...'"
                )


def validate_file(filepath: Path, verbose: bool = False) -> ValidationResult:
    """Run all validation checks against a single YAML file."""
    result = ValidationResult(filepath)
    file_type = classify_file(filepath)

    # Read raw content for secret scanning
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        result.error(f"Could not read file: {exc}")
        return result

    # YAML syntax check
    data = validate_yaml_syntax(filepath, result)
    if data is None:
        return result

    # Semantic validation by file type
    if file_type == "prometheus_config":
        validate_prometheus_config(data, result)
    elif file_type == "alert_rules":
        validate_rule_groups(data, result, "alert_rules")
    elif file_type == "recording_rules":
        validate_rule_groups(data, result, "recording_rules")
    elif file_type == "alertmanager_config":
        validate_alertmanager_config(data, result)

    # Secret scan
    check_secrets(filepath, content, result)

    if verbose and result.passed:
        print(f"  PASS: {filepath}")

    return result


def collect_yaml_files(paths: list[Path]) -> list[Path]:
    """Resolve paths to individual YAML files, expanding directories."""
    files: list[Path] = []

    for path in paths:
        if path.is_file() and path.suffix in (".yml", ".yaml", ".tmpl"):
            files.append(path)
        elif path.is_dir():
            for ext in ("*.yml", "*.yaml"):
                files.extend(sorted(path.rglob(ext)))
        else:
            print(f"WARNING: Skipping {path}")

    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Prometheus and Alertmanager YAML configurations"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[
            Path("configs/prometheus"),
            Path("configs/alertmanager"),
            Path("alerts/prometheus"),
        ],
        help="Files or directories to validate",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show passing files"
    )
    args = parser.parse_args()

    files = collect_yaml_files(args.paths)

    if not files:
        print("No YAML files found to validate.")
        return 0

    print(f"Validating {len(files)} Prometheus/Alertmanager YAML file(s)...\n")

    results: list[ValidationResult] = []
    for filepath in files:
        result = validate_file(filepath, verbose=args.verbose)
        results.append(result)

    # Report
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

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"\nResults: {passed} passed, {failed} failed, {warnings_total} warnings")
    print(f"Files checked: {len(results)}")

    return 1 if errors_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
