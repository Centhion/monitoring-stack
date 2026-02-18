# Dashboard Customization Guide

This guide covers the structure, conventions, and modification procedures for the Grafana dashboards in this repository. All dashboards are provisioned via configuration-as-code and should be modified in Git, not through the Grafana UI.

---

## Dashboard Inventory

| Dashboard | File | UID | Purpose |
|-----------|------|-----|---------|
| Windows Server Overview | `dashboards/windows/windows_overview.json` | `windows-overview` | Per-server Windows metrics: CPU, memory, disk, network, services |
| Linux Server Overview | `dashboards/linux/linux_overview.json` | `linux-overview` | Per-server Linux metrics: CPU, memory, disk, network, systemd |
| Infrastructure Overview | `dashboards/overview/infrastructure_overview.json` | `infra-overview` | Fleet-wide health, top-N problem servers, alert summary |
| Log Explorer | `dashboards/overview/log_explorer.json` | `log-explorer` | Unified log search across Windows Event Log and Linux journal |

---

## Architecture

### Provisioning Flow

Grafana loads dashboards from disk using the provisioning config at `configs/grafana/dashboards/dashboards.yml`. This config maps three filesystem paths to Grafana folders:

| Folder in Grafana | Filesystem Path | Dashboard Source |
|-------------------|-----------------|------------------|
| Windows | `/var/lib/grafana/dashboards/windows` | `dashboards/windows/*.json` |
| Linux | `/var/lib/grafana/dashboards/linux` | `dashboards/linux/*.json` |
| Overview | `/var/lib/grafana/dashboards/overview` | `dashboards/overview/*.json` |

When Grafana starts, it reads all JSON files from these directories and creates/updates the corresponding dashboards. Changes made through the Grafana UI are overwritten on the next restart because `allowUiUpdates` is false.

### Datasource References

All dashboards reference datasources by UID rather than by name. This ensures portability across environments.

| Datasource | UID | Type | Provisioned By |
|------------|-----|------|----------------|
| Prometheus | `prometheus` | prometheus | `configs/grafana/datasources/datasources.yml` |
| Loki | `loki` | loki | `configs/grafana/datasources/datasources.yml` |

Every panel target in the dashboard JSON contains a `datasource` block:

```json
{
  "datasource": {
    "type": "prometheus",
    "uid": "prometheus"
  }
}
```

If you deploy additional Prometheus or Loki instances, add them to the datasources provisioning file and reference them by their UID in dashboard panels.

### Recording Rules Dependency

The Windows and Linux overview dashboards query pre-computed recording rules rather than raw metrics. This improves query performance at scale and ensures consistent calculations across dashboards and alerts.

Recording rules are defined in `configs/prometheus/recording_rules.yml`. The naming convention is:

```
<scope>:<metric_description>:<aggregation>
```

| Recording Rule | Used By | Raw Metric Source |
|----------------|---------|-------------------|
| `instance:windows_cpu_utilization:ratio` | Windows Overview | `windows_cpu_time_total` |
| `instance:windows_memory_utilization:ratio` | Windows Overview | `windows_memory_physical_free_bytes` / `windows_memory_physical_total_bytes` |
| `instance:windows_disk_free:ratio` | Windows Overview | `windows_logical_disk_free_bytes` / `windows_logical_disk_size_bytes` |
| `instance:windows_disk_io_utilization:ratio` | Windows Overview | `windows_logical_disk_idle_seconds_total` |
| `instance:windows_network_bytes:rate5m` | Windows Overview | `windows_net_bytes_total` |
| `instance:windows_services_not_running:count` | Windows Overview | `windows_service_state` |
| `instance:windows_uptime:seconds` | Windows Overview | `windows_time_current_timestamp_seconds` - `windows_system_boot_time_timestamp` |
| `instance:linux_cpu_utilization:ratio` | Linux Overview | `node_cpu_seconds_total` |
| `instance:linux_memory_utilization:ratio` | Linux Overview | `node_memory_MemAvailable_bytes` / `node_memory_MemTotal_bytes` |
| `instance:linux_disk_free:ratio` | Linux Overview | `node_filesystem_avail_bytes` / `node_filesystem_size_bytes` |
| `instance:linux_disk_io_utilization:ratio` | Linux Overview | `node_disk_io_time_seconds_total` |
| `instance:linux_network_bytes:rate5m` | Linux Overview | `node_network_receive_bytes_total` + `node_network_transmit_bytes_total` |
| `instance:linux_load_normalized:ratio` | Linux Overview | `node_load1` / CPU count |
| `instance:linux_systemd_failed:count` | Linux Overview | `node_systemd_unit_state` |
| `instance:linux_uptime:seconds` | Linux Overview | `time()` - `node_boot_time_seconds` |
| `fleet:servers_reporting:count` | Infra Overview | `up` |
| `fleet:cpu_utilization:avg` | Infra Overview | Avg of instance CPU rules |
| `fleet:memory_utilization:avg` | Infra Overview | Avg of instance memory rules |
| `fleet:high_cpu:count` | Infra Overview | Count where CPU > 85% |
| `fleet:low_disk:count` | Infra Overview | Count where disk free < 20% |

If you rename or remove a recording rule, you must update the corresponding dashboard panels.

---

## Template Variables

All dashboards use Grafana template variables for filtering. These appear as dropdowns at the top of each dashboard.

### Common Variables

| Variable | Type | Query | Multi-Select | Include All |
|----------|------|-------|--------------|-------------|
| `environment` | Query | `label_values(environment)` | Yes | Yes |
| `datacenter` | Query | `label_values(datacenter)` | Yes | Yes |
| `hostname` | Query | `label_values({environment=~"$environment"}, hostname)` | Yes | Yes |
| `role` | Query | `label_values(role)` | Yes | Yes |

### OS-Specific Filtering

The Windows dashboard filters hostname by `os="windows"`:
```
label_values({os="windows", environment=~"$environment"}, hostname)
```

The Linux dashboard filters by `os="linux"`:
```
label_values({os="linux", environment=~"$environment"}, hostname)
```

### Log Explorer Variables

The Log Explorer adds two additional variables:

| Variable | Type | Purpose |
|----------|------|---------|
| `os` | Custom | Values: `windows`, `linux`. Filters log streams by operating system |
| `search` | Text Box | Free-text search applied as regex filter (`\|~ "$search"`) |

---

## Standard Label Taxonomy

All metrics and logs carry five standard labels applied by the Alloy agent (`configs/alloy/common/labels.alloy`):

| Label | Source | Description |
|-------|--------|-------------|
| `environment` | `ENVIRONMENT` env var | Deployment environment (production, staging, development) |
| `datacenter` | `DATACENTER` env var | Physical or logical datacenter identifier |
| `role` | `SERVER_ROLE` env var | Server role (dc, sql, iis, fileserver, docker, base) |
| `os` | Alloy relabel rule | Operating system (windows, linux) |
| `hostname` | `HOSTNAME` env var | Server hostname |

When writing PromQL or LogQL queries for dashboards, always filter by these labels using template variable references (e.g., `{hostname=~"$hostname", environment=~"$environment"}`).

---

## Customization Procedures

### Adding a New Panel

1. Open the dashboard JSON file in your editor.
2. Locate the `panels` array (or find the target row's nested `panels`).
3. Add a new panel object. Copy an existing panel of the same type as a template.
4. Assign a unique `id` (increment from the highest existing ID in the file).
5. Set the `gridPos` to position the panel (x: 0-23 column, y: row position, w: width 1-24, h: height).
6. Configure the `targets` array with your PromQL or LogQL query.
7. Validate the JSON: `python scripts/validate_dashboards.py` (once Phase 5 tooling is built).
8. Commit via the `/commit` workflow.

Example panel structure:

```json
{
  "id": 50,
  "type": "timeseries",
  "title": "My Custom Metric",
  "datasource": {
    "type": "prometheus",
    "uid": "prometheus"
  },
  "gridPos": { "x": 0, "y": 20, "w": 12, "h": 8 },
  "targets": [
    {
      "expr": "instance:windows_cpu_utilization:ratio{hostname=~\"$hostname\"} * 100",
      "legendFormat": "{{hostname}}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "color": "green", "value": null },
          { "color": "yellow", "value": 75 },
          { "color": "red", "value": 90 }
        ]
      }
    }
  }
}
```

### Adding a New Dashboard

1. Create a JSON file in the appropriate directory:
   - `dashboards/windows/` for Windows-specific dashboards
   - `dashboards/linux/` for Linux-specific dashboards
   - `dashboards/overview/` for cross-platform or fleet dashboards
2. Use a unique `uid` (lowercase, hyphenated, e.g., `windows-sql-detail`).
3. Include the standard template variables (environment, datacenter, hostname, role).
4. Reference datasources by UID (`prometheus` or `loki`).
5. The provisioning config (`configs/grafana/dashboards/dashboards.yml`) already watches these directories, so no provisioning changes are needed unless you add a new folder.
6. Validate and commit.

### Adding a New Dashboard Folder

If you need a new Grafana folder (e.g., `dashboards/roles/` for role-specific dashboards):

1. Create the directory: `mkdir dashboards/roles`
2. Add a provider entry to `configs/grafana/dashboards/dashboards.yml`:

```yaml
- name: "Roles"
  orgId: 1
  folder: "Roles"
  type: file
  disableDeletion: true
  allowUiUpdates: false
  options:
    path: /var/lib/grafana/dashboards/roles
    foldersFromFilesStructure: false
```

3. Update `ARCHITECTURE.md` to include the new directory.
4. Create your dashboard JSON files in the new directory.

### Modifying Thresholds

Thresholds control panel coloring (green/yellow/red). They are defined in each panel's `fieldConfig.defaults.thresholds`:

```json
"thresholds": {
  "mode": "absolute",
  "steps": [
    { "color": "green", "value": null },
    { "color": "yellow", "value": 75 },
    { "color": "red", "value": 90 }
  ]
}
```

- `value: null` is the base color (applied when no threshold is exceeded).
- Each subsequent step applies when the value is >= the step value.
- For percentage metrics (CPU, memory, disk), standard thresholds are 75% warning and 90% critical.
- Adjust these to match your organization's SLAs.

### Modifying Time Ranges and Refresh

Default time ranges and refresh intervals are set in the dashboard JSON root:

```json
{
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "refresh": "30s"
}
```

Common time ranges: `now-1h`, `now-6h`, `now-24h`, `now-7d`. Users can override these in the Grafana UI without affecting the provisioned default.

---

## Panel Type Reference

| Panel Type | Use Case | Key Config |
|------------|----------|------------|
| `stat` | Single value (CPU %, server count) | `fieldConfig.defaults.unit`, `thresholds` |
| `timeseries` | Time-series graphs | `targets[].expr`, `fieldConfig.defaults.unit` |
| `table` | Tabular data (service lists, top-N) | `transformations`, `fieldConfig.overrides` |
| `logs` | Log stream display (Loki) | `targets[].expr` (LogQL), `options.showLabels` |
| `bargauge` | Horizontal bar comparison | `targets[].expr`, `options.orientation` |
| `row` | Section separator | `title`, `collapsed` |

---

## Unit Reference

Commonly used Grafana units in this project:

| Unit String | Display | Used For |
|-------------|---------|----------|
| `percent` | 75% | CPU, memory, disk utilization |
| `percentunit` | 0.75 -> 75% | Raw ratio values (auto-converts 0-1 to 0-100%) |
| `Bps` | 1.5 MB/s | Network throughput, disk I/O |
| `bytes` | 1.5 GB | Memory totals, disk sizes |
| `s` | 3600 -> 1h | Durations |
| `d` | 7 | Uptime in days |
| `short` | 1,234 | Generic counts |
| `none` | Raw value | Dimensionless values |

---

## Troubleshooting

### Dashboard Not Appearing

1. Verify the JSON file is in the correct directory under `dashboards/`.
2. Check the provisioning config maps the directory to the correct Grafana mount path.
3. Verify the JSON is syntactically valid: `python scripts/validate_dashboards.py`.
4. Check Grafana logs for provisioning errors: `kubectl logs <grafana-pod> | grep provision`.

### No Data in Panels

1. Verify the datasource UID matches: `prometheus` for metrics, `loki` for logs.
2. Confirm recording rules are loaded: query `instance:windows_cpu_utilization:ratio` directly in Grafana Explore.
3. Check that template variables resolve: open the variable dropdown and confirm values appear.
4. Verify the Alloy agent is sending data: check `up{job="windows_base"}` or `up{job="linux_base"}`.

### Template Variables Empty

1. Variables depend on label values existing in the data. If no servers are reporting, dropdowns will be empty.
2. Check variable queries in the dashboard JSON under `templating.list[].query`.
3. Ensure the variable regex and datasource UID are correct.

### Panels Show "No Data" After Rule Change

If you modified a recording rule name in `configs/prometheus/recording_rules.yml`, update every dashboard panel that references the old name. Search the dashboard JSON files for the old metric name to find affected panels.

---

## Development Workflow

1. Edit the dashboard JSON file in your editor.
2. Validate: `python scripts/validate_dashboards.py` (Phase 5).
3. Commit via `/commit` workflow (triggers dashboard-reviewer agent).
4. Deploy to Grafana by updating the mounted volume or restarting the pod.
5. Verify in the Grafana UI that panels render correctly.

For rapid iteration during development, you can temporarily set `allowUiUpdates: true` in the provisioning YAML, make changes in the Grafana UI, then export the JSON and commit it. Remember to set `allowUiUpdates` back to `false` before deploying to production.

---

*Last Updated: 2026-02-18*
