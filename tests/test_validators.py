#!/usr/bin/env python3
"""
Test suite for configuration validators.

Runs each validator against known-good and known-bad fixtures to verify
that validators correctly identify valid configs and catch errors.

Usage:
    python -m pytest tests/test_validators.py -v
    python tests/test_validators.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
PYTHON = sys.executable


def run_validator(script: str, target: str) -> tuple[int, str]:
    """Execute a validator script and return (exit_code, output)."""
    cmd = [PYTHON, str(PROJECT_ROOT / "scripts" / script), target]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(PROJECT_ROOT),
    )
    return proc.returncode, proc.stdout + proc.stderr


# ---------------------------------------------------------------------------
# Alloy Validator Tests
# ---------------------------------------------------------------------------

class TestAlloyValidator:
    """Tests for scripts/validate_alloy.py."""

    def test_valid_alloy_passes(self):
        """A structurally correct Alloy config should pass validation."""
        code, output = run_validator(
            "validate_alloy.py",
            str(FIXTURES_DIR / "valid_alloy.alloy"),
        )
        assert code == 0, f"Expected exit 0, got {code}. Output:\n{output}"

    def test_unbalanced_braces_fails(self):
        """An Alloy config with unbalanced braces should fail."""
        code, output = run_validator(
            "validate_alloy.py",
            str(FIXTURES_DIR / "invalid_alloy_braces.alloy"),
        )
        assert code == 1, f"Expected exit 1, got {code}. Output:\n{output}"
        assert "brace" in output.lower() or "unbalanced" in output.lower(), (
            f"Expected brace error in output:\n{output}"
        )

    def test_project_alloy_configs_pass(self):
        """All Alloy configs in the project should pass validation."""
        alloy_dir = PROJECT_ROOT / "configs" / "alloy"
        if not alloy_dir.exists():
            return  # Skip if configs not yet built
        code, output = run_validator("validate_alloy.py", str(alloy_dir))
        assert code == 0, f"Project Alloy configs failed:\n{output}"


# ---------------------------------------------------------------------------
# Prometheus/Alertmanager Validator Tests
# ---------------------------------------------------------------------------

class TestPrometheusValidator:
    """Tests for scripts/validate_prometheus.py."""

    def test_valid_alert_rules_pass(self):
        """Well-formed alert rules should pass validation."""
        code, output = run_validator(
            "validate_prometheus.py",
            str(FIXTURES_DIR / "valid_alert_rules.yml"),
        )
        assert code == 0, f"Expected exit 0, got {code}. Output:\n{output}"

    def test_invalid_alert_rules_fail(self):
        """Alert rules with missing fields and bad durations should fail."""
        code, output = run_validator(
            "validate_prometheus.py",
            str(FIXTURES_DIR / "invalid_alert_rules.yml"),
        )
        assert code == 1, f"Expected exit 1, got {code}. Output:\n{output}"

    def test_project_prometheus_configs_pass(self):
        """All Prometheus configs in the project should pass validation."""
        prom_dir = PROJECT_ROOT / "configs" / "prometheus"
        if not prom_dir.exists():
            return
        code, output = run_validator("validate_prometheus.py", str(prom_dir))
        assert code == 0, f"Project Prometheus configs failed:\n{output}"

    def test_project_alert_rules_pass(self):
        """All alert rules in the project should pass validation."""
        alerts_dir = PROJECT_ROOT / "alerts" / "prometheus"
        if not alerts_dir.exists():
            return
        code, output = run_validator("validate_prometheus.py", str(alerts_dir))
        assert code == 0, f"Project alert rules failed:\n{output}"

    def test_project_alertmanager_config_passes(self):
        """The Alertmanager config should pass validation."""
        am_dir = PROJECT_ROOT / "configs" / "alertmanager"
        if not am_dir.exists():
            return
        code, output = run_validator("validate_prometheus.py", str(am_dir))
        assert code == 0, f"Alertmanager config failed:\n{output}"


# ---------------------------------------------------------------------------
# Dashboard Validator Tests
# ---------------------------------------------------------------------------

class TestDashboardValidator:
    """Tests for scripts/validate_dashboards.py."""

    def test_valid_dashboard_passes(self):
        """A well-formed dashboard JSON should pass validation."""
        code, output = run_validator(
            "validate_dashboards.py",
            str(FIXTURES_DIR / "valid_dashboard.json"),
        )
        assert code == 0, f"Expected exit 0, got {code}. Output:\n{output}"

    def test_invalid_dashboard_fails(self):
        """A dashboard with bad datasource UID should report errors."""
        code, output = run_validator(
            "validate_dashboards.py",
            str(FIXTURES_DIR / "invalid_dashboard.json"),
        )
        # The invalid dashboard has a nonexistent datasource UID and missing uid field
        assert code == 1, f"Expected exit 1, got {code}. Output:\n{output}"

    def test_project_dashboards_pass(self):
        """All dashboards in the project should pass validation."""
        dash_dir = PROJECT_ROOT / "dashboards"
        if not dash_dir.exists():
            return
        code, output = run_validator("validate_dashboards.py", str(dash_dir))
        assert code == 0, f"Project dashboards failed:\n{output}"


# ---------------------------------------------------------------------------
# Unified Runner Tests
# ---------------------------------------------------------------------------

class TestUnifiedRunner:
    """Tests for scripts/validate_all.py."""

    def test_runner_executes_without_crash(self):
        """The unified runner should complete without crashing."""
        code, output = run_validator("validate_all.py", "--verbose")
        # The runner may report warnings but should not crash
        assert "Traceback" not in output, f"Runner crashed:\n{output}"


# ---------------------------------------------------------------------------
# Manual test runner (for environments without pytest)
# ---------------------------------------------------------------------------

def run_all_tests() -> int:
    """Execute all test methods and report results."""
    test_classes = [
        TestAlloyValidator,
        TestPrometheusValidator,
        TestDashboardValidator,
        TestUnifiedRunner,
    ]

    total = 0
    passed = 0
    failed = 0
    failures: list[str] = []

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]

        for method_name in methods:
            total += 1
            test_id = f"{cls.__name__}.{method_name}"

            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  PASS: {test_id}")
            except AssertionError as exc:
                failed += 1
                failures.append(f"{test_id}: {exc}")
                print(f"  FAIL: {test_id}")
            except Exception as exc:
                failed += 1
                failures.append(f"{test_id}: {type(exc).__name__}: {exc}")
                print(f"  ERROR: {test_id}")

    print(f"\n{passed}/{total} passed, {failed} failed")

    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
