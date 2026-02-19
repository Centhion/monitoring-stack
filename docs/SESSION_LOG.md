# Session Log

This file maintains continuity across work sessions. Each session summary is appended here using the `/handoff` command.

## How to Use

**End of session**: Run `/handoff` to generate and save a summary.

**Start of session**: Read the most recent entry to restore context.

---

## Session History

<!-- New sessions are appended below this line -->

---

## Session: 2026-02-18 (Continued Session -- PoC Fixes + Fleet Deployment Planning)

### Completed

- **Log Explorer Loki parse error fix**: Changed `allValue` from `".*"` to `".+"` in `dashboards/overview/log_explorer.json` for all template variables. Loki rejects `.*` as a label matcher because it matches empty strings; `.+` requires at least one character. Grafana restarted and re-provisioned.

- **Phase 5.7 planning complete**: Designed and approved the Fleet Tagging and Ansible Deployment Tooling plan. Updated `docs/PROJECT_PLAN.md` with full Phase 5.7 task breakdown (6 deliverables), architecture notes, risks, and human actions required.

- **(From earlier in this continued session -- already committed)**:
  - `6da1cb7`: Fixed `${VAR:-default}` env var substitution in Prometheus and Alertmanager configs (literal Docker service names)
  - `e23e90b`: Fixed Alloy River syntax (`service = {` to `service {}`), removed deprecated `cs` collector, added job relabel rules for Alloy v1.13
  - `9582c73`: Updated recording rules and all references for Alloy v1.13 metric renames (`windows_cs_*` to `windows_memory_*`, `windows_os_*` to `windows_time_*`/`windows_system_*`)
  - `be31f2c`: Replaced env var URLs with literal URLs in Grafana datasource provisioning
  - `c2be8f4`: Converted dashboard template variable `query` from object format to string format, added `allValue` and default `current`

- **All changes committed and pushed**: `01cec68` -- Log Explorer allValue fix, Phase 5.7 plan, session log. Pre-commit check caught Grafana password in SESSION_LOG.md; redacted before commit.

- **User confirmed dashboards working**: Log Explorer and other dashboards showing data. Full pipeline validated end-to-end.

### Blockers

- **MSI Alloy service still running**: The MSI-installed Alloy Windows service is still running on the user's workstation alongside the standalone binary. Needs admin terminal to run `net stop Alloy; sc config Alloy start= disabled`. Not blocking development, but should be cleaned up.

- **Phase 5.7 human dependencies**: Cannot begin implementation tasks #4-5 (Ansible playbook, tag validation) without: datacenter site list with metadata, host inventory export, production Prometheus/Loki URLs, and test servers with WinRM/SSH access.

### Decisions Made

- **Site code format**: Short abbreviations (DV, SOL, SN, etc.) -- final format confirmed by user. Many more sites to come beyond the initial examples.
- **Multi-role support**: `roles` field in hosts.yml is a list. ALLOY_ROLE env var set to primary (first) role. All matching role_*.alloy files deployed to config directory.
- **OS build precision**: Free-form string, not enum-constrained. Captures exact build numbers (e.g., `"10.0.20348"` for Server 2022, `"9.5"` for RHEL 9.5).
- **Ansible first**: Ansible chosen over SCCM for initial deployment tooling. SCCM support can be added later.
- **Role vocabulary**: `dc, sql, iis, fileserver, docker, generic, exchange, print, app` -- extensible via sites.yml with documented process. `hyperv` explicitly excluded per user.
- **Site metadata fields**: timezone, AD domain, network segment tracked per site (not per host). Inherited via site code reference.
- **Host metadata fields**: os_type and os_build tracked per host.
- **Loki `allValue` must use `.+` not `.*`**: Loki requires at least one non-empty-compatible matcher in every query. Prometheus dashboards can use either, but `.+` is safer for both.

### Next Session

1. **Begin Phase 5.7 Task 1**: Create `inventory/sites.yml` with schema, example entries (DV, SOL, SN), and role/OS vocabulary. Include extension documentation.
2. **Begin Phase 5.7 Task 2**: Create `inventory/hosts.yml` with schema and example entries demonstrating multi-role servers, multiple OS types, and precise OS builds.
3. **Begin Phase 5.7 Task 3**: Create `scripts/fleet_inventory.py` with validate, import-csv, generate-ansible, and stats subcommands.
4. **Phase 5.7 Tasks 4-6** (Ansible playbook, tag validation, onboarding runbook) can proceed in parallel with tasks 1-3 but will need human inputs (site list, host inventory) before they can be fully tested.

### Context

- **Alloy binary location**: `C:\Tools\alloy\alloy-windows-amd64.exe` (standalone zip, not MSI)
- **Alloy run command**: `C:\Tools\alloy\alloy-windows-amd64.exe run C:\Docker_testing\Monitoring_Dashboarding\configs\alloy\local\`
- **Docker containers**: `mon-prometheus`, `mon-grafana`, `mon-loki`, `mon-alertmanager` -- all healthy
- **Grafana credentials**: `admin` / `[REDACTED -- see local .env or team vault]`
- **Python path**: `C:/Users/etamez/AppData/Local/Programs/Python/Python314/python.exe`
- **Commit method**: `C:/Users/etamez/AppData/Local/Programs/Python/Python314/python.exe skills/git_smart_commit.py commit-and-push "message"` (direct `git commit` blocked by settings.json)
- **Alloy v1.13 key changes**: `cs` collector removed (metrics in memory/os/cpu), River block syntax (`service {}` not `service = {}`), job label forced to `integrations/windows` (relabel rule overrides), `env()` stdlib function deprecated (use `sys.env()`)
- **Domain consolidation**: ~16 AD domains merging to 1 over next 18 months. Inventory design is AD-independent by design.
- **Fleet scale**: 500-2000 servers across 5-15+ sites. Moderate cardinality, no concerns.

---
