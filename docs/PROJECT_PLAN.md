# Project Plan

> This file is the agent's primary task tracker. Update it after completing significant work.

**Project Goal**: Build an enterprise-grade monitoring and dashboarding platform using the Grafana observability stack (Alloy, Prometheus, Loki, Alertmanager, Grafana) to replace Microsoft SCOM and Squared Up for mixed Windows/Linux server environments.

---

## Project Status Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: Project Setup | Completed | Template hydration and repo configuration |
| Phase 1: Alloy Agent Configs | Completed | 13 configs: common (3), Windows base+4 roles (6), Linux base+docker (3), deployment guide (1) |
| Phase 2: Backend Configs (Prometheus + Loki) | Completed | 6 tasks: Prometheus config + recording rules, Loki config, Grafana provisioning, docs |
| Phase 3: Alerting Rules and Routing | Completed | 8 tasks: 46 alert rules, Alertmanager routing + Teams template, Grafana notifiers, runbooks |
| Phase 4: Grafana Dashboards | Completed | 4 dashboards (Windows, Linux, Infra Overview, Log Explorer) + customization guide |
| Phase 5: Validation Tooling | Completed | 3 validators + runner, 12/12 tests passing, requirements.txt, docs |
| Phase 5.5: Docker Compose PoC | In Progress | Local testing stack via Docker Desktop (pre-K8s validation) |
| Phase 6: Mimir Migration | Pending | Long-term metrics storage (when ready to scale) |

**Status Key**: Pending | In Progress | Completed | Blocked

---

## Phase 0: Project Setup

**Goal**: Hydrate the Golden Template with project-specific configuration, documentation, and agent setup.

**Status**: Completed

### Tasks

- [x] Approve tech stack (Alloy, Prometheus, Loki, Alertmanager, Grafana, Mimir Phase 2)
- [x] Create README.md with project overview
- [x] Create ARCHITECTURE.md with stack details and data flow
- [x] Create project directory structure (configs/, dashboards/, alerts/, scripts/)
- [x] Create project-specific agents (config-validator, dashboard-reviewer, alert-rule-auditor)
- [x] Update .claude/settings.json with project permissions
- [x] Create .env.example with required environment variables
- [x] Clean up template artifacts (remove onboarding protocol from CLAUDE.md)
- [x] Add PostToolUse hooks for automatic config validation
- [x] Create scripts/validate_on_save.py for hook-based validation
- [x] Initialize Git repository with remote configured

### Human Actions Required

- [x] Set up Git remote (https://github.com/Centhion/Monitoring_Dashboarding.git)
- [x] Push initial commit
- [x] Verify Git authentication (HTTPS with credential manager)

---

## Phase 1: Alloy Agent Configurations

**Goal**: Create production-ready Grafana Alloy configurations for Windows and Linux servers with role-specific collection profiles, standard label taxonomy, and modular architecture.

**Status**: Completed

**Architecture**: Modular directory-based configs. Alloy loads all `.alloy` files in a directory via `alloy run <dir>`. Deploy common/ + os/base + os/logs + role files per server.

**Config Syntax**: Alloy syntax (HCL-inspired, formerly River). File extension: `.alloy`. Environment variables via `sys.env()`.

### Tasks -- Common Components

- [x] 1. Define standard label taxonomy (environment, datacenter, role, os, hostname) -- `configs/alloy/common/labels.alloy`
- [x] 2. Create Prometheus remote_write endpoint -- `configs/alloy/common/remote_write.alloy`
- [x] 3. Create Loki push endpoint -- `configs/alloy/common/loki_push.alloy`

### Tasks -- Windows Configs

- [x] 4. Create Windows base OS metrics (CPU, memory, disk, network, services) -- `configs/alloy/windows/base.alloy`
- [x] 5. Create Windows Event Log collection (System, Application, Security) -- `configs/alloy/windows/logs_eventlog.alloy`
- [x] 6. Create Windows role: Domain Controller (AD DS, replication, DNS, Kerberos) -- `configs/alloy/windows/role_dc.alloy`
- [x] 7. Create Windows role: SQL Server (perf counters, database metrics, error logs) -- `configs/alloy/windows/role_sql.alloy`
- [x] 8. Create Windows role: IIS Web Server (requests, app pools, error rates, IIS logs) -- `configs/alloy/windows/role_iis.alloy`
- [x] 9. Create Windows role: File Server (SMB sessions, DFS, disk I/O) -- `configs/alloy/windows/role_fileserver.alloy`

### Tasks -- Linux Configs

- [x] 10. Create Linux base OS metrics (CPU, memory, disk, network, systemd) -- `configs/alloy/linux/base.alloy`
- [x] 11. Create Linux journal log collection -- `configs/alloy/linux/logs_journal.alloy`
- [x] 12. Create Linux role: Docker host (container metrics, container logs) -- `configs/alloy/linux/role_docker.alloy`

### Tasks -- Documentation

- [x] 13. Create Alloy deployment guide for Windows and Linux -- `docs/ALLOY_DEPLOYMENT.md`

### Risks

- SQL Server perf counters may need custom WMI queries if `prometheus.exporter.mssql` is unavailable in Alloy
- DC metrics depend on AD DS role being installed on the target server
- Component label uniqueness required across files loaded in same directory

### Human Actions Required

- [ ] Deploy Alloy to one test Windows server (any role)
- [ ] Deploy Alloy to one test Linux server
- [ ] Provide endpoint URLs for Prometheus and Loki (when Phase 2 backends are deployed)
- [ ] Confirm list of Windows services to monitor per role (or accept defaults)

---

## Phase 2: Backend Configurations (Prometheus + Loki)

**Goal**: Production-ready server-side configs for Prometheus and Loki, including retention policies, recording rules, ingestion limits, and Grafana provisioning.

**Status**: Completed

### Tasks

- [x] 1. Create Prometheus server config (global, scrape, remote_write receiver, retention) -- `configs/prometheus/prometheus.yml`
- [x] 2. Create Prometheus recording rules (pre-computed aggregations for dashboard performance) -- `configs/prometheus/recording_rules.yml`
- [x] 3. Create Loki server config (storage, retention, limits, schema) -- `configs/loki/loki.yml`
- [x] 4. Create Grafana datasource provisioning (Prometheus + Loki endpoints) -- `configs/grafana/datasources/datasources.yml`
- [x] 5. Create Grafana dashboard provisioning (point to dashboards/ directory) -- `configs/grafana/dashboards/dashboards.yml`
- [x] 6. Document backend deployment requirements -- `docs/BACKEND_DEPLOYMENT.md`

### Implementation Notes

- Prometheus: 30d retention, 50GB size limit, WAL compression, remote_write receiver enabled
- Recording rules: 3 groups (Windows, Linux, Fleet) with pre-computed CPU/memory/disk/network aggregations
- Loki: Schema v13, TSDB store, 720h retention, 10MB/s ingestion limit, 10K stream limit
- Grafana: Datasource UIDs (prometheus, loki) used by all dashboards for portability

### Human Actions Required (Deferred Until Cluster Ready)

- [ ] Deploy Prometheus to Kubernetes cluster
- [ ] Deploy Loki to Kubernetes cluster
- [ ] Configure persistent storage volumes
- [ ] Verify data ingestion from Alloy agents

---

## Phase 3: Alerting Rules and Routing

**Goal**: Comprehensive alert rules for Windows and Linux servers based on industry best practices, Alertmanager routing with Teams integration, and operational runbook stubs.

**Status**: Completed

### Tasks

- [x] 7. Create Windows server alert rules (CPU, memory, disk, services, uptime) -- `alerts/prometheus/windows_alerts.yml`
- [x] 8. Create Linux server alert rules (CPU, memory, disk, systemd, load) -- `alerts/prometheus/linux_alerts.yml`
- [x] 9. Create infrastructure alert rules (Prometheus/Loki/Alertmanager health, fleet anomalies) -- `alerts/prometheus/infra_alerts.yml`
- [x] 10. Create role-specific alert rules (AD replication, SQL health, IIS errors, Docker daemon) -- `alerts/prometheus/role_alerts.yml`
- [x] 11. Create Alertmanager config (routing tree, receivers, grouping, inhibition) -- `configs/alertmanager/alertmanager.yml`
- [x] 12. Create Alertmanager Teams webhook template (Adaptive Card format) -- `configs/alertmanager/templates/teams.tmpl`
- [x] 13. Create Grafana notification provisioning (contact points, policies) -- `configs/grafana/notifiers/notifiers.yml`
- [x] 14. Document alert runbooks with investigation and remediation steps -- `docs/ALERT_RUNBOOKS.md`

### Implementation Notes

- 46 total alert rules across 4 files: Windows (10), Linux (13), Infrastructure (10), Role-specific (14)
- Alert rules reference recording rules from Phase 2 for consistent metric naming
- Alertmanager routing: critical -> Teams + email, warning -> Teams, info -> Teams (separate channel)
- Inhibition rules: server down suppresses warnings; notification failures suppress fleet alerts
- Teams template uses Adaptive Card JSON for rich formatting with severity, host, environment facts
- Full runbooks with investigation commands and remediation steps for every alert

### Human Actions Required (Deferred Until Cluster Ready)

- [ ] Create Teams Incoming Webhook in monitoring channel
- [ ] Deploy Alertmanager to Kubernetes cluster
- [ ] Test alert delivery to Teams channel
- [ ] Review and approve alert thresholds
- [ ] Provide SCOM monitor export for gap analysis (optional, can add later)

---

## Phase 4: Grafana Dashboards

**Goal**: Pre-built dashboard JSON files querying the exact metrics from our Alloy configs, with template variables for fleet-wide filtering.

**Status**: Completed

### Tasks

- [x] 15. Build Windows Server overview dashboard (CPU, memory, disk, network, services) -- `dashboards/windows/windows_overview.json`
- [x] 16. Build Linux Server overview dashboard (CPU, memory, disk, network, systemd) -- `dashboards/linux/linux_overview.json`
- [x] 17. Build Infrastructure Overview dashboard (fleet health, top-N, alert summary) -- `dashboards/overview/infrastructure_overview.json`
- [x] 18. Build Log Explorer dashboard (unified log search across Windows Event Log + Linux journal) -- `dashboards/overview/log_explorer.json`
- [x] 19. Document dashboard customization guide -- `docs/DASHBOARD_GUIDE.md`

### Implementation Notes

- Windows overview: 18 panels across 5 rows (overview stats, CPU/memory, disk, network, services)
- Linux overview: 23 panels across 6 rows (overview stats, CPU/load, memory/swap, disk, network, systemd)
- Infrastructure overview: 21 panels across 5 rows (fleet health, trends, top-N problems, alerts, availability)
- Log Explorer: 7 panels using LogQL against Loki (volume graphs, Windows/Linux log streams, unified search)
- All dashboards use recording rule metrics for consistent queries
- Template variables: environment, datacenter, hostname, role (multi-select with All option)
- Datasource UIDs: prometheus, loki (matching provisioning config)

### Human Actions Required (Deferred Until Cluster Ready)

- [ ] Deploy Grafana to Kubernetes cluster
- [ ] Configure Grafana authentication (AD/LDAP integration)
- [ ] Review dashboards with operations team
- [ ] Provide feedback on layout and metric selection

---

## Phase 5: Validation Tooling

**Goal**: Python scripts to validate all config types before deployment, runnable locally and in CI.

**Status**: Completed

### Tasks

- [x] 20. Create Alloy config validator (syntax structure, required components, env var usage) -- `scripts/validate_alloy.py`
- [x] 21. Create Prometheus/Alertmanager YAML validator (schema, required fields, label compliance) -- `scripts/validate_prometheus.py`
- [x] 22. Create Grafana dashboard JSON validator (schema, template vars, panel completeness) -- `scripts/validate_dashboards.py`
- [x] 23. Create unified validation runner (runs all validators, outputs report) -- `scripts/validate_all.py`
- [x] 24. Create test fixtures and expected outputs -- `tests/`
- [x] 25. Create requirements.txt for validation dependencies -- `requirements.txt`
- [x] 26. Document tooling usage -- `docs/VALIDATION_TOOLING.md`

### Implementation Notes

- Alloy validator: brace balancing, required component patterns, duplicate labels, hardcoded endpoints/secrets
- Prometheus validator: YAML syntax, rule group structure, duration formats, receiver/route consistency
- Dashboard validator: JSON syntax, UID uniqueness, datasource references, template vars, grid overlap detection
- Unified runner: orchestrates all validators, supports --verbose and --strict modes
- Test suite: 12 tests (fixtures for valid + invalid configs per validator type), all passing
- PyYAML is the only external dependency (requirements.txt)

### Human Actions Required (Deferred Until CI Pipeline Ready)

- [ ] Integrate validation into CI/CD pipeline

---

## Phase 5.5: Docker Compose PoC Environment

**Goal**: Spin up the full monitoring stack locally via Docker Desktop to validate configs, dashboards, alert routing, and the Alloy-to-backend data pipeline before deploying to Kubernetes.

**Status**: In Progress

**Resource Budget**: ~2 GB RAM total (memory-limited containers for developer workstations)

### Tasks

- [ ] 1. Create `docker-compose.yml` with Prometheus, Loki, Alertmanager, Grafana -- volume mounts, memory limits, health checks
- [ ] 2. Create `docker-compose.override.yml` for local dev (debug ports, verbose logging)
- [ ] 3. Create `.dockerignore` to exclude non-essential files
- [ ] 4. Create local Alloy config for Windows host pointing at Docker stack -- `configs/alloy/local/`
- [ ] 5. Create `scripts/poc_setup.py` for one-command startup with health validation
- [ ] 6. Create `docs/LOCAL_TESTING.md` step-by-step guide
- [ ] 7. Update PROJECT_PLAN.md to mark phase complete

### Risks

- Memory pressure on developer workstation (mitigated with container limits)
- Alloy Windows binary collector names may differ from documentation (validate during local testing)
- Teams webhook requires real URL for notification testing (fallback: stdout logging)

### Human Actions Required

- [ ] Ensure Docker Desktop is installed and running
- [ ] Download Grafana Alloy Windows binary (optional, for end-to-end testing)
- [ ] Create Teams webhook URL (optional, alerts log to stdout as fallback)

---

## Phase 6: Mimir Migration (Future)

**Goal**: Replace Prometheus with Grafana Mimir for long-term metric storage and horizontal scaling.

**Status**: Pending

### Tasks

- [ ] Create Mimir server configuration
- [ ] Configure object storage backend (S3 or Azure Blob)
- [ ] Update Alloy remote_write targets to point to Mimir
- [ ] Migrate recording rules from Prometheus to Mimir ruler
- [ ] Validate dashboard queries work against Mimir
- [ ] Performance test at expected scale

### Human Actions Required

- [ ] Provision object storage bucket
- [ ] Deploy Mimir to Kubernetes cluster
- [ ] Decommission standalone Prometheus
- [ ] Validate retention and query performance

---

## Human Actions Checklist

> Consolidated list of all actions requiring human intervention.

### Prerequisites

- [x] Set up Git remote (https://github.com/Centhion/Monitoring_Dashboarding.git)
- [x] Push initial commit
- [x] Verify Git authentication (HTTPS)
- [ ] Create Teams Incoming Webhook for monitoring channel
- [ ] Provide SCOM monitor export/list for alert parity audit

### During Development

- [ ] Deploy Alloy to test Windows server
- [ ] Deploy Alloy to test Linux server
- [ ] Deploy Prometheus, Loki, Alertmanager, Grafana to Kubernetes cluster
- [ ] Configure persistent storage volumes
- [ ] Configure Grafana authentication (AD/LDAP)
- [ ] Test alert delivery end-to-end
- [ ] Review and approve alert thresholds
- [ ] Review dashboards with operations team

### Post-Completion

- [ ] Integrate config validation into CI/CD pipeline
- [ ] Document operational runbooks
- [ ] Plan Mimir migration timeline
- [ ] Decommission SCOM/Squared Up (when ready)

---

## Notes

- Alloy replaces both node_exporter/windows_exporter and Promtail in a single binary
- All configs designed to work with both Prometheus (Phase 1) and Mimir (Phase 2) via remote_write
- Teams notification via Alertmanager webhook -- no MCP or external tooling required
- Python 3.10+ required for validation scripts

---

*Document Version: 1.0*
*Last Updated: 2026-02-18*
