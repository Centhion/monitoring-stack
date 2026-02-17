# Project Plan

> This file is the agent's primary task tracker. Update it after completing significant work.

**Project Goal**: Build an enterprise-grade monitoring and dashboarding platform using the Grafana observability stack (Alloy, Prometheus, Loki, Alertmanager, Grafana) to replace Microsoft SCOM and Squared Up for mixed Windows/Linux server environments.

---

## Project Status Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: Project Setup | In Progress | Template hydration and repo configuration |
| Phase 1: Alloy Agent Configs | Pending | Windows and Linux agent configurations |
| Phase 2: Backend Configs (Prometheus + Loki) | Pending | Server-side metric and log storage configs |
| Phase 3: Alerting Rules and Routing | Pending | SCOM parity alerts, Alertmanager routing, Teams integration |
| Phase 4: Grafana Dashboards | Pending | Dashboard JSON definitions and provisioning |
| Phase 5: Validation Tooling | Pending | Python scripts for config linting and testing |
| Phase 6: Mimir Migration | Pending | Long-term metrics storage (when ready to scale) |

**Status Key**: Pending | In Progress | Completed | Blocked

---

## Phase 0: Project Setup

**Goal**: Hydrate the Golden Template with project-specific configuration, documentation, and agent setup.

**Status**: In Progress

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

- [x] Set up Git remote (git@github.com:Centhion/Monitoring_Dashboarding.git)
- [ ] Push initial commit
- [ ] Verify SSH authentication works (`ssh -T git@github.com`)

---

## Phase 1: Alloy Agent Configurations

**Goal**: Create production-ready Grafana Alloy configurations for both Windows and Linux servers that collect system metrics and forward logs.

**Status**: Pending

### Tasks

- [ ] Create base Alloy config with common components (remote_write, loki push)
- [ ] Create Windows-specific Alloy config (windows_exporter integration, Windows Event Log)
- [ ] Create Linux-specific Alloy config (node_exporter integration, journal/syslog)
- [ ] Define standard label taxonomy (environment, datacenter, role, os, hostname)
- [ ] Document Alloy deployment instructions for both OS types
- [ ] Create config validation script for Alloy configs

### Human Actions Required

- [ ] Deploy Alloy to test Windows server
- [ ] Deploy Alloy to test Linux server
- [ ] Verify metrics appear in Prometheus
- [ ] Verify logs appear in Loki

---

## Phase 2: Backend Configurations (Prometheus + Loki)

**Goal**: Configure Prometheus and Loki server-side settings including retention, storage, and recording rules.

**Status**: Pending

### Tasks

- [ ] Create Prometheus server configuration (scrape configs, retention, storage)
- [ ] Create Prometheus recording rules for common aggregations
- [ ] Create Loki server configuration (storage, retention, limits)
- [ ] Define log parsing pipelines in Loki (structured metadata extraction)
- [ ] Document backend deployment requirements

### Human Actions Required

- [ ] Deploy Prometheus to Kubernetes cluster
- [ ] Deploy Loki to Kubernetes cluster
- [ ] Configure persistent storage volumes
- [ ] Verify data ingestion from Alloy agents

---

## Phase 3: Alerting Rules and Routing

**Goal**: Build alert rules that achieve parity with critical SCOM monitors, configure Alertmanager routing, and integrate Teams notifications.

**Status**: Pending

### Tasks

- [ ] Audit existing SCOM monitors and identify critical alerts to replicate
- [ ] Create Prometheus alerting rules for Windows servers (CPU, memory, disk, services)
- [ ] Create Prometheus alerting rules for Linux servers (CPU, memory, disk, systemd)
- [ ] Create Prometheus alerting rules for infrastructure (connectivity, DNS, NTP)
- [ ] Configure Alertmanager routing tree (severity-based routing)
- [ ] Configure Alertmanager receivers (Teams webhook, email fallback)
- [ ] Configure alert grouping and inhibition rules
- [ ] Create Grafana contact points and notification policies
- [ ] Document alert runbooks for each critical alert

### Human Actions Required

- [ ] Create Teams Incoming Webhook in monitoring channel
- [ ] Provide SCOM monitor export/list for audit
- [ ] Deploy Alertmanager to Kubernetes cluster
- [ ] Test alert delivery to Teams channel
- [ ] Review and approve alert thresholds

---

## Phase 4: Grafana Dashboards

**Goal**: Create comprehensive Grafana dashboards for Windows Server, Linux Server, and infrastructure overview.

**Status**: Pending

### Tasks

- [ ] Create Grafana datasource provisioning YAML (Prometheus + Loki)
- [ ] Create dashboard provisioning YAML (point to dashboards/ directory)
- [ ] Build Windows Server overview dashboard (CPU, memory, disk, network, services)
- [ ] Build Linux Server overview dashboard (CPU, memory, disk, network, systemd)
- [ ] Build Infrastructure Overview dashboard (fleet health, top-N, alert summary)
- [ ] Build Log Explorer dashboard (integrated log search with metric correlation)
- [ ] Create dashboard variables (environment, datacenter, hostname filters)
- [ ] Document dashboard customization guide

### Human Actions Required

- [ ] Deploy Grafana to Kubernetes cluster
- [ ] Configure Grafana authentication (AD/LDAP integration)
- [ ] Review dashboards with operations team
- [ ] Provide feedback on layout and metric selection

---

## Phase 5: Validation Tooling

**Goal**: Build Python scripts to validate configurations, lint dashboards, and test alert rules before deployment.

**Status**: Pending

### Tasks

- [ ] Create config validator for Alloy configs (syntax + required fields)
- [ ] Create config validator for Prometheus rules (promtool integration)
- [ ] Create dashboard JSON schema validator
- [ ] Create alert rule coverage checker (compare against SCOM monitor list)
- [ ] Set up test fixtures and expected outputs
- [ ] Document tooling usage

### Human Actions Required

- [ ] Integrate validation into CI/CD pipeline

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

- [x] Set up Git remote (git@github.com:Centhion/Monitoring_Dashboarding.git)
- [ ] Push initial commit
- [ ] Verify SSH authentication
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
*Last Updated: 2026-02-17*
