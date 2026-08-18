"""
Python Custom Prometheus Metrics Exporter (DEVOPS-22)
Collects platform health, synthetic latencies, storage quotas, and certificate expiries.
"""

import time
import logging
import random
from prometheus_client import start_http_server, Gauge, Counter, Histogram

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Prometheus Metrics Definitions
CERT_EXPIRY_DAYS = Gauge(
    "platform_cert_expiry_days",
    "Days remaining until TLS certificate expires",
    ["domain"]
)

STORAGE_QUOTA_RATIO = Gauge(
    "platform_storage_quota_ratio",
    "Current object storage capacity utilization ratio (0.0 to 1.0)",
    ["bucket"]
)

SYNTHETIC_LATENCY = Histogram(
    "platform_synthetic_latency_seconds",
    "Synthetic probe round-trip latency to critical platform services",
    ["service"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)
)

PROCESSED_EVENTS = Counter(
    "platform_processed_events_total",
    "Total platform telemetry and GitOps events processed",
    ["service", "status"]
)

PLATFORM_HEALTH = Gauge(
    "platform_service_health",
    "Health status of internal platform components (1=Healthy, 0=Degraded)",
    ["component"]
)

SERVICES = ["argocd", "openbao", "artifactory", "seaweedfs", "loki", "velero"]
DOMAINS = ["argocd.codeforge.local", "openbao.codeforge.local", "artifactory.codeforge.local", "grafana.codeforge.local"]
BUCKETS = ["loki-data", "velero-backups"]

def collect_telemetry():
    """Simulates background telemetry collection and updates Prometheus metrics."""
    logging.info("Gathering platform metrics...")
    
    # 1. Update Certificate Expiry Days
    for domain in DOMAINS:
        # Simulated certificate validity between 45 and 85 days
        days = random.randint(45, 85)
        CERT_EXPIRY_DAYS.labels(domain=domain).set(days)
    
    # 2. Update Storage Quota
    for bucket in BUCKETS:
        # Simulated usage ratio between 0.12 and 0.45
        ratio = round(random.uniform(0.12, 0.45), 3)
        STORAGE_QUOTA_RATIO.labels(bucket=bucket).set(ratio)

    # 3. Update Health Status & Latency
    for service in SERVICES:
        latency = round(random.uniform(0.008, 0.065), 4)
        SYNTHETIC_LATENCY.labels(service=service).observe(latency)
        PLATFORM_HEALTH.labels(component=service).set(1)
        PROCESSED_EVENTS.labels(service=service, status="success").inc(random.randint(1, 5))

def main():
    port = 8080
    logging.info(f"Starting Python Custom Metrics Exporter on port {port}...")
    start_http_server(port)
    logging.info(f"Metrics endpoint available at http://0.0.0.0:{port}/metrics")
    
    while True:
        try:
            collect_telemetry()
        except Exception as e:
            logging.error(f"Error during metrics collection: {e}")
        time.sleep(15)

if __name__ == "__main__":
    main()
