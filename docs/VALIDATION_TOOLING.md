# Validation Tooling

This document describes the configuration validation scripts that check all monitoring configs before deployment. Validators can run locally during development and in CI pipelines.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all validators
python scripts/validate_all.py

# Run with verbose output (show passing files)
python scripts/validate_all.py --verbose

# Run in strict mode (warnings treated as errors)
python scripts/validate_all.py --strict

# Run specific validators only
python scripts/validate_all.py --only alloy prometheus
python scripts/validate_all.py --only dashboards
```

---

## Validators

### Alloy Config Validator (`scripts/validate_alloy.py`)

Validates Grafana Alloy configuration files (.alloy). Alloy uses a custom HCL-inspired syntax, so this validator performs structural checks rather than full grammar parsing.

**Checks performed:**
- Balanced braces (block nesting)
- Required components present for each file category (common, windows, linux)
- Environment variable usage via `sys.env()` instead of hardcoded values
- Duplicate component labels within a single file
- No hardcoded endpoint URLs
- No hardcoded secrets (passwords, tokens, API keys)

**Usage:**
```bash
python scripts/validate_alloy.py                           # All Alloy configs
python scripts/validate_alloy.py configs/alloy/windows/    # Windows configs only
python scripts/validate_alloy.py configs/alloy/common/labels.alloy  # Single file
```

**Required component patterns by directory:**

| Directory | File | Required Patterns |
|-----------|------|-------------------|
| common | labels.alloy | `prometheus.relabel`, `loki.process` |
| common | remote_write.alloy | `prometheus.remote_write`, `sys.env(` |
| common | loki_push.alloy | `loki.write`, `sys.env(` |
| windows | base.alloy | `prometheus.exporter.windows`, `prometheus.scrape`, `forward_to` |
| windows | logs_eventlog.alloy | `loki.source.windowsevent`, `forward_to` |
| linux | base.alloy | `prometheus.exporter.unix`, `prometheus.scrape`, `forward_to` |
| linux | logs_journal.alloy | `loki.source.journal`, `forward_to` |

---

### Prometheus/Alertmanager Validator (`scripts/validate_prometheus.py`)

Validates YAML configurations for Prometheus server, recording rules, alert rules, and Alertmanager.

**Checks performed:**
- YAML syntax validity
- Required top-level keys present (global, groups, route, receivers)
- Alert rule structure: `alert`, `expr`, `for`, `labels.severity`, `annotations`
- Recording rule naming convention: `namespace:metric:aggregation`
- Duration format validation (5m, 1h, 30s)
- Group name uniqueness
- Job name uniqueness in scrape_configs
- Alertmanager route-receiver consistency (no dangling references)
- Inhibition rule completeness
- No hardcoded secrets

**Usage:**
```bash
python scripts/validate_prometheus.py                      # All Prometheus + Alertmanager
python scripts/validate_prometheus.py alerts/prometheus/    # Alert rules only
python scripts/validate_prometheus.py configs/alertmanager/ # Alertmanager only
```

**Auto-classification:** The validator determines file type from the filename and path:
- `prometheus.yml` -- Prometheus server config
- `recording_rules.yml` -- Recording rules
- `alertmanager.yml` -- Alertmanager config
- Files under `alerts/` -- Alert rules
- Files under `configs/grafana/` -- Grafana provisioning (syntax-only)

---

### Dashboard Validator (`scripts/validate_dashboards.py`)

Validates Grafana dashboard JSON files for structure, conventions, and correctness.

**Checks performed:**
- JSON syntax validity
- Required metadata: `uid`, `title`, `schemaVersion`, `tags`
- UID uniqueness across all dashboard files
- Template variables present: `environment`, `datacenter`
- Panel structure: `targets`, `datasource`, `gridPos`
- Datasource UID references match provisioned sources (`prometheus`, `loki`)
- Grid position overlap detection
- Recording rule metric name validation

**Usage:**
```bash
python scripts/validate_dashboards.py                      # All dashboards
python scripts/validate_dashboards.py dashboards/windows/  # Windows dashboards
python scripts/validate_dashboards.py dashboards/overview/log_explorer.json  # Single file
```

**Known datasource UIDs:** `prometheus`, `loki`, `-- Grafana --`, `-- Dashboard --`

---

### Unified Runner (`scripts/validate_all.py`)

Orchestrates all validators and produces a combined report.

**Execution order:**
1. Alloy Configs (`configs/alloy/`)
2. Prometheus/Alertmanager YAML (`configs/prometheus/`, `configs/alertmanager/`, `alerts/prometheus/`)
3. Grafana Provisioning YAML (`configs/grafana/`)
4. Grafana Dashboards (`dashboards/`)

**Flags:**

| Flag | Description |
|------|-------------|
| `--verbose` / `-v` | Show passing files in addition to failures |
| `--strict` | Treat warnings as errors (exit 1 if any warnings) |
| `--only <key> [...]` | Run specific validators: `alloy`, `prometheus`, `grafana-provisioning`, `dashboards` |

**Exit codes:**
- `0` -- All validators passed
- `1` -- One or more validators reported errors (or warnings in strict mode)

---

## Test Suite

Test fixtures and a test runner validate the validators themselves.

**Structure:**
```
tests/
  __init__.py
  test_validators.py          # Test cases for all validators
  fixtures/
    valid_alloy.alloy          # Clean Alloy config (should pass)
    invalid_alloy_braces.alloy # Unbalanced braces (should fail)
    valid_alert_rules.yml      # Clean alert rules (should pass)
    invalid_alert_rules.yml    # Missing fields, bad duration (should fail)
    valid_dashboard.json       # Clean dashboard (should pass)
    invalid_dashboard.json     # Bad datasource UID (should fail)
```

**Running tests:**
```bash
# With pytest (recommended)
python -m pytest tests/test_validators.py -v

# Without pytest (built-in runner)
python tests/test_validators.py
```

**Test categories:**

| Test Class | Validates |
|------------|-----------|
| `TestAlloyValidator` | Valid configs pass, unbalanced braces fail, project configs pass |
| `TestPrometheusValidator` | Valid rules pass, invalid rules fail, project configs pass |
| `TestDashboardValidator` | Valid JSON passes, bad datasource fails, project dashboards pass |
| `TestUnifiedRunner` | Runner completes without crash |

---

## CI Integration

### GitHub Actions Example

```yaml
name: Validate Configs
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run validators
        run: python scripts/validate_all.py --strict

      - name: Run tests
        run: python -m pytest tests/test_validators.py -v
```

### Pre-Commit Hook

The `scripts/validate_on_save.py` script runs automatically via git hooks or editor integration for fast syntax checks during development. The full validators (`validate_all.py`) provide deeper semantic validation before committing and in CI.

---

## Adding Custom Validators

To add a new validator:

1. Create a script in `scripts/` following the pattern of existing validators.
2. Accept file paths or directories as positional arguments.
3. Support `--verbose` flag for detailed output.
4. Return exit code 0 for success, 1 for failure.
5. Print errors as `ERROR:` and warnings as `WARN:` for consistent parsing.
6. Add the validator to the `VALIDATORS` list in `scripts/validate_all.py`.
7. Add test fixtures in `tests/fixtures/` and test cases in `tests/test_validators.py`.

---

## Severity Levels

| Level | Meaning | Exit Code |
|-------|---------|-----------|
| ERROR | Structural or semantic issue that will cause deployment failure | 1 |
| WARN | Convention violation or potential issue that may work but is not recommended | 0 (1 in strict mode) |
| PASS | File passed all checks | 0 |

---

*Last Updated: 2026-02-18*
