# Enterprise Monitoring and Dashboarding Platform

A configuration-as-code repository for an enterprise-grade monitoring and dashboarding solution built on the Grafana observability stack. Replaces Microsoft SCOM and Squared Up with a modern, scalable alternative for mixed Windows and Linux server environments.

## Purpose

Provide centralized infrastructure monitoring, log aggregation, alerting, and dashboarding for enterprise Windows and Linux servers using open-source tooling. All configurations -- dashboards, alert rules, agent configs, and provisioning -- are version-controlled and reproducible.

## Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| Agent | Grafana Alloy | Unified telemetry collector on every server (metrics + logs) |
| Metrics | Prometheus (Phase 1), Mimir (Phase 2) | Time-series metrics ingestion and querying |
| Logs | Loki | Label-based log aggregation |
| Alerting | Alertmanager + Grafana Alerting | Alert routing, grouping, deduplication, notifications |
| Visualization | Grafana | Dashboards, exploration, alert management UI |
| Notifications | Microsoft Teams (webhook) | Alert delivery to operations team |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Centhion/Monitoring_Dashboarding.git
cd Monitoring_Dashboarding

# Set up environment
cp .env.example .env
# Edit .env with your environment-specific values (webhook URLs, endpoints, etc.)
```

## Structure

| Directory | Purpose |
|-----------|---------|
| `configs/alloy/` | Grafana Alloy agent configurations (Windows and Linux) |
| `configs/prometheus/` | Prometheus server configuration and recording rules |
| `configs/loki/` | Loki server configuration |
| `configs/alertmanager/` | Alertmanager routing, receivers, and inhibition rules |
| `configs/grafana/` | Grafana provisioning (datasources, dashboards, notifiers) |
| `dashboards/` | Grafana dashboard JSON definitions |
| `alerts/` | Prometheus alerting rules and Grafana alert policies |
| `scripts/` | Python tooling for config validation, generation, and testing |
| `docs/` | Architecture docs, runbooks, and project tracking |
| `.claude/` | Agent configuration (instructions, skills, agents, rules, commands) |
| `skills/` | Universal helper scripts (Python) |

## Features

- **Configuration as Code**: All monitoring configs, dashboards, and alert rules stored in Git
- **Mixed OS Support**: Alloy agent configs for both Windows Server and Linux
- **SCOM Parity Alerts**: Alert rules designed to replicate critical SCOM monitors
- **Teams Integration**: Alert notifications delivered to Microsoft Teams channels
- **Grafana Provisioning**: Datasources, dashboards, and contact points deployed via provisioning YAML
- **Validation Tooling**: Python scripts to lint and validate configs before deployment

## Documentation

- See `ARCHITECTURE.md` for design patterns, stack details, and decisions
- See `docs/PROJECT_PLAN.md` for current status and task tracking
- See `docs/ALLOY_DEPLOYMENT.md` for Alloy agent deployment on Windows and Linux
- See `docs/BACKEND_DEPLOYMENT.md` for Prometheus, Loki, Alertmanager, and Grafana deployment
- See `docs/ALERT_RUNBOOKS.md` for alert investigation and remediation procedures
- See `docs/DASHBOARD_GUIDE.md` for dashboard customization and creation
- See `docs/VALIDATION_TOOLING.md` for config validation scripts and CI integration

## Development

This project uses Claude Code with the following commands:

| Command | Description |
|---------|-------------|
| `/setup` | Initial project configuration |
| `/status` | Show Git state and active tasks |
| `/commit` | Generate a commit message |
| `/plan` | Design implementation approach |
| `/handoff` | Generate session summary |

## License

(Add your license here)
