# Backend Deployment Guide

This guide covers deploying Prometheus, Loki, Alertmanager, and Grafana to Kubernetes using the configuration files from this repository.

## Prerequisites

- Kubernetes cluster with kubectl access
- Persistent volume provisioner (for TSDB and log storage)
- Network connectivity from Alloy agents to the cluster (ports 9090, 3100, 9093, 3000)

## Architecture

```
Alloy agents (Windows/Linux servers)
    |
    |  remote_write (port 9090)
    v
+-------------------+
| Prometheus        |  <-- configs/prometheus/prometheus.yml
| (metrics TSDB)    |  <-- configs/prometheus/recording_rules.yml
+--------+----------+  <-- alerts/prometheus/*.yml
         |
         |  alert rules fire
         v
+--------+----------+
| Alertmanager      |  <-- configs/alertmanager/alertmanager.yml
| (routing/notify)  |  <-- configs/alertmanager/templates/teams.tmpl
+--------+----------+
         |
         |  webhook
         v
  Microsoft Teams

Alloy agents (Windows/Linux servers)
    |
    |  loki push (port 3100)
    v
+-------------------+
| Loki              |  <-- configs/loki/loki.yml
| (log storage)     |
+-------------------+

+-------------------+
| Grafana           |  <-- configs/grafana/datasources/datasources.yml
| (dashboards)      |  <-- configs/grafana/dashboards/dashboards.yml
+-------------------+  <-- configs/grafana/notifiers/notifiers.yml
                       <-- dashboards/**/*.json
```

## Component Deployment

### Prometheus

**Config files to mount:**

| Source | Mount Path |
|--------|-----------|
| `configs/prometheus/prometheus.yml` | `/etc/prometheus/prometheus.yml` |
| `configs/prometheus/recording_rules.yml` | `/etc/prometheus/rules/recording_rules.yml` |
| `alerts/prometheus/windows_alerts.yml` | `/etc/prometheus/rules/windows_alerts.yml` |
| `alerts/prometheus/linux_alerts.yml` | `/etc/prometheus/rules/linux_alerts.yml` |
| `alerts/prometheus/infra_alerts.yml` | `/etc/prometheus/rules/infra_alerts.yml` |
| `alerts/prometheus/role_alerts.yml` | `/etc/prometheus/rules/role_alerts.yml` |

**Required startup flags:**

```
--config.file=/etc/prometheus/prometheus.yml
--web.enable-remote-write-receiver
--storage.tsdb.path=/prometheus/data
--storage.tsdb.retention.time=30d
--storage.tsdb.retention.size=50GB
--storage.tsdb.wal-compression
--web.enable-lifecycle
```

**Storage requirements:**
- Persistent volume: 50-100GB (depends on fleet size and retention)
- Mount at: `/prometheus/data`

**Environment variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLUSTER_NAME` | `monitoring` | External label for federation |
| `POD_NAME` | `prometheus-0` | Replica identification |
| `ALERTMANAGER_HOST` | `alertmanager` | Alertmanager service hostname |
| `ALERTMANAGER_PORT` | `9093` | Alertmanager service port |
| `LOKI_HOST` | `loki` | Loki service hostname (for scraping Loki metrics) |
| `LOKI_PORT` | `3100` | Loki service port |
| `GRAFANA_HOST` | `grafana` | Grafana service hostname |
| `GRAFANA_PORT` | `3000` | Grafana service port |

**Ports:**
- 9090: HTTP API and web UI

---

### Loki

**Config files to mount:**

| Source | Mount Path |
|--------|-----------|
| `configs/loki/loki.yml` | `/etc/loki/loki.yml` |

**Storage requirements:**
- Persistent volume: 50-200GB (depends on log volume and retention)
- Mount at: `/loki` (contains chunks, index, compactor directories)

**Ports:**
- 3100: HTTP API (push and query)
- 9096: gRPC (internal)

---

### Alertmanager

**Config files to mount:**

| Source | Mount Path |
|--------|-----------|
| `configs/alertmanager/alertmanager.yml` | `/etc/alertmanager/alertmanager.yml` |
| `configs/alertmanager/templates/teams.tmpl` | `/etc/alertmanager/templates/teams.tmpl` |

**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `TEAMS_WEBHOOK_URL` | Microsoft Teams incoming webhook URL |
| `SMTP_HOST` | SMTP server for email fallback |
| `SMTP_PORT` | SMTP port |
| `SMTP_FROM` | Sender address for alert emails |
| `ALERT_EMAIL_TO` | Recipient address for alert emails |

**Ports:**
- 9093: HTTP API and web UI

---

### Grafana

**Config files to mount:**

| Source | Mount Path |
|--------|-----------|
| `configs/grafana/datasources/datasources.yml` | `/etc/grafana/provisioning/datasources/datasources.yml` |
| `configs/grafana/dashboards/dashboards.yml` | `/etc/grafana/provisioning/dashboards/dashboards.yml` |
| `configs/grafana/notifiers/notifiers.yml` | `/etc/grafana/provisioning/notifiers/notifiers.yml` |
| `dashboards/windows/*.json` | `/var/lib/grafana/dashboards/windows/` |
| `dashboards/linux/*.json` | `/var/lib/grafana/dashboards/linux/` |
| `dashboards/overview/*.json` | `/var/lib/grafana/dashboards/overview/` |

**Environment variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `PROMETHEUS_URL` | `http://prometheus:9090` | Prometheus datasource URL |
| `LOKI_URL` | `http://loki:3100` | Loki datasource URL |
| `GF_SECURITY_ADMIN_PASSWORD` | (must set) | Initial admin password |

**Ports:**
- 3000: HTTP web UI

---

## Deployment Order

Deploy in this order to satisfy dependencies:

1. **Loki** -- No dependencies. Starts accepting logs immediately.
2. **Prometheus** -- No dependencies. Starts accepting remote_write immediately.
3. **Alertmanager** -- No dependencies. Referenced by Prometheus for alert routing.
4. **Grafana** -- Depends on Prometheus and Loki being reachable for datasource health checks.
5. **Alloy agents** -- Deploy to servers after backends are confirmed running.

## Validation After Deployment

| Check | How |
|-------|-----|
| Prometheus is running | `curl http://prometheus:9090/-/healthy` |
| Prometheus accepts remote_write | `curl -X POST http://prometheus:9090/api/v1/write` (expect 400, not 404) |
| Loki is running | `curl http://loki:3100/ready` |
| Alertmanager is running | `curl http://alertmanager:9093/-/healthy` |
| Grafana is running | `curl http://grafana:3000/api/health` |
| Datasources connected | Grafana UI > Configuration > Data Sources > Test all |
| Metrics flowing | Grafana Explore > Prometheus > query `up` |
| Logs flowing | Grafana Explore > Loki > query `{source="eventlog"}` or `{source="journal"}` |

## Network Requirements

| From | To | Port | Protocol | Purpose |
|------|----|------|----------|---------|
| Alloy agents | Prometheus | 9090 | HTTP | Metrics remote_write |
| Alloy agents | Loki | 3100 | HTTP | Log push |
| Prometheus | Alertmanager | 9093 | HTTP | Alert delivery |
| Alertmanager | Teams webhook | 443 | HTTPS | Notification delivery |
| Grafana | Prometheus | 9090 | HTTP | Metric queries |
| Grafana | Loki | 3100 | HTTP | Log queries |
| Users | Grafana | 3000 | HTTP/S | Dashboard access |
