
# Redis Exporter Setup

This document explains how to install and configure **Redis Exporter** for monitoring Redis instances using **Prometheus**.

The provided script:

- Downloads and installs `redis_exporter`
- Creates **systemd services** for Redis instances
- Exposes metrics on dedicated ports
- Enables Prometheus scraping

---

# Script: `setup_redis_exporter.sh`

Run the script as follows:

```bash
./setup_redis_exporter.sh --host YOUR_SERVER_IP_OR_HOSTNAME
```

Example:

```bash
sudo ./setup_redis_exporter.sh --host localhost
```

---

# What This Script Does

The script performs the following tasks automatically:

1. Downloads **redis_exporter**
2. Installs it under:

```
/opt/redis_exporter
```

3. Creates **three systemd services** for Redis instances:

| Redis Port | Exporter Port |
|-------------|--------------|
| 7001 | 9121 |
| 7002 | 9122 |
| 7003 | 9123 |

4. Enables and starts the services.

5. Allows **Prometheus to scrape Redis metrics**.

---

# Script Usage

```bash
sudo ./setup_redis_exporter.sh --host <redis_host> [--bind <bind_ip>] [--redis-user <user>] [--redis-pass <password>]
```

---

# Examples

### Basic Installation

```bash
sudo ./setup_redis_exporter.sh --host localhost
```

### Bind Exporter to All Interfaces

```bash
sudo ./setup_redis_exporter.sh --host 127.0.0.1 --bind 0.0.0.0
```

### With Redis Authentication (User + Password)

```bash
sudo ./setup_redis_exporter.sh --host localhost --redis-user monitoring --redis-pass 'secret'
```

### With Redis Password Only

```bash
sudo ./setup_redis_exporter.sh --host localhost --redis-pass 'secret'
```

---

# Exporter Installation Details

Installed version:

```
redis_exporter v1.58.0
```

Download source:

```
https://github.com/oliver006/redis_exporter
```

Installed location:

```
/opt/redis_exporter/redis_exporter
```

---

# Systemd Services

The script creates the following services:

```
redis-exporter-7001.service
redis-exporter-7002.service
redis-exporter-7003.service
```

Service location:

```
/etc/systemd/system/
```

---

# Checking Service Status

```bash
systemctl status redis-exporter-7001
systemctl status redis-exporter-7002
systemctl status redis-exporter-7003
```

---

# Checking Listening Ports

```bash
ss -tunlp | egrep ':(9121|9122|9123)'
```

---

# Testing Metrics Endpoint

```bash
curl http://127.0.0.1:9121/metrics
curl http://127.0.0.1:9122/metrics
curl http://127.0.0.1:9123/metrics
```

Example metric check:

```bash
curl -s http://127.0.0.1:9121/metrics | grep redis_connected_clients
```

---

# Prometheus Configuration Example

```yaml
- job_name: redis
  static_configs:
    - targets:
        - server:9121
        - server:9122
        - server:9123
```

Replace `server` with the Redis server hostname.

Example:

```
mytest.test.my.domain.local:9121
```

---

# Example Metrics

Some example Redis metrics exposed:

```
redis_connected_clients
redis_memory_used_bytes
redis_keyspace_hits_total
redis_keyspace_misses_total
redis_commands_processed_total
```

These metrics can be visualized in **Grafana dashboards**.

