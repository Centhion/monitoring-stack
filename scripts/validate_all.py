#!/usr/bin/env python3
"""
Unified Validation Runner

Orchestrates all config validators and produces a combined report. Designed to
run locally during development and in CI pipelines before deployment.

Validators executed:
  1. Alloy config validator   (scripts/validate_alloy.py)
  2. Prometheus/Alertmanager   (scripts/validate_prometheus.py)
  3. Grafana dashboard JSON    (scripts/validate_dashboards.py)
  4. Grafana provisioning YAML (syntax-only via validate_prometheus.py)

Exit codes:
    0 -- All validators passed
    1 -- One or more validators reported errors

Usage:
    python scripts/validate_all.py [--verbose] [--strict]
    python scripts/validate_all.py --only alloy prometheus
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Resolve the project root relative to this script's location.
# This allows the runner to work regardless of the working directory.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Python interpreter -- use the same interpreter that is running this script
# to ensure validators can import the same packages.
PYTHON = sys.executable

# Validator definitions: name, script path, default target paths
VALIDATORS = [
    {
        "name": "Alloy Configs",
        "script": SCRIPT_DIR / "validate_alloy.py",
        "targets": [PROJECT_ROOT / "configs" / "alloy"],
        "key": "alloy",
    },
    {
        "name": "Prometheus/Alertmanager YAML",
        "script": SCRIPT_DIR / "validate_prometheus.py",
        "targets": [
            PROJECT_ROOT / "configs" / "prometheus",
            PROJECT_ROOT / "configs" / "alertmanager",
            PROJECT_ROOT / "alerts" / "prometheus",
        ],
        "key": "prometheus",
    },
    {
        "name": "Grafana Provisioning YAML",
        "script": SCRIPT_DIR / "validate_prometheus.py",
        "targets": [
            PROJECT_ROOT / "configs" / "grafana",
        ],
        "key": "grafana-provisioning",
    },
    {
        "name": "Grafana Dashboards",
        "script": SCRIPT_DIR / "validate_dashboards.py",
        "targets": [PROJECT_ROOT / "dashboards"],
        "key": "dashboards",
    },
]


def run_validator(
    validator: dict, verbose: bool = False
) -> tuple[str, int, str, float]:
    """Execute a single validator as a subprocess.

    Returns a tuple of (name, exit_code, output, duration_seconds).
    """
    name = validator["name"]
    script = validator["script"]
    targets = validator["targets"]

    # Only include targets that exist on disk
    existing_targets = [str(t) for t in targets if t.exists()]

    if not existing_targets:
        return name, 0, f"  Skipped: no target directories found\n", 0.0

    if not script.exists():
        return name, 1, f"  ERROR: Validator script not found: {script}\n", 0.0

    cmd = [PYTHON, str(script)]
    if verbose:
        cmd.append("--verbose")
    cmd.extend(existing_targets)

    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        duration = time.monotonic() - start
        output = proc.stdout
        if proc.stderr:
            output += proc.stderr
        return name, proc.returncode, output, duration

    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return name, 1, f"  ERROR: Validator timed out after 120s\n", duration
    except FileNotFoundError as exc:
        return name, 1, f"  ERROR: {exc}\n", 0.0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all configuration validators"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Pass --verbose to each validator"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as errors (non-zero exit if any warnings)"
    )
    parser.add_argument(
        "--only", nargs="+",
        choices=[v["key"] for v in VALIDATORS],
        help="Run only specific validators"
    )
    args = parser.parse_args()

    # Filter validators if --only specified
    validators_to_run = VALIDATORS
    if args.only:
        validators_to_run = [v for v in VALIDATORS if v["key"] in args.only]

    separator = "=" * 72
    print(separator)
    print("  Configuration Validation Report")
    print(separator)
    print()

    overall_exit = 0
    total_duration = 0.0
    summary_lines: list[str] = []

    for validator in validators_to_run:
        name, exit_code, output, duration = run_validator(
            validator, verbose=args.verbose
        )
        total_duration += duration

        status = "PASS" if exit_code == 0 else "FAIL"
        status_indicator = "[PASS]" if exit_code == 0 else "[FAIL]"

        print(f"--- {name} {status_indicator} ({duration:.1f}s) ---")
        if output.strip():
            # Indent validator output for readability
            for line in output.strip().splitlines():
                print(f"  {line}")
        print()

        if exit_code != 0:
            overall_exit = 1

        # Check for warnings in strict mode
        if args.strict and "WARN" in output:
            overall_exit = 1
            status = "FAIL (strict)"

        summary_lines.append(f"  {status_indicator} {name} ({duration:.1f}s)")

    # Final summary
    print(separator)
    print("  Summary")
    print(separator)
    for line in summary_lines:
        print(line)
    print()
    print(f"  Total time: {total_duration:.1f}s")

    if overall_exit == 0:
        print("  Overall: ALL VALIDATIONS PASSED")
    else:
        print("  Overall: VALIDATION FAILURES DETECTED")

    print(separator)

    return overall_exit


if __name__ == "__main__":
    sys.exit(main())
