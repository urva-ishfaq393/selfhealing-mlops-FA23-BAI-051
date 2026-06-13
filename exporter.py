#!/usr/bin/env python3
import time
import requests
from prometheus_client import start_http_server, Gauge

CONFIDENCE_GAUGE = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from the Sentiment Analysis API'
)

APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5
EXPORTER_PORT = 8000
DEFAULT_CONFIDENCE = 1.0

def fetch_confidence():
    try:
        response = requests.get(APP_URL, timeout=4)
        response.raise_for_status()
        data = response.json()
        return float(data.get("confidence", DEFAULT_CONFIDENCE))
    except Exception as e:
        print(f"[WARN] Could not reach app: {e}. Using default {DEFAULT_CONFIDENCE}")
        return DEFAULT_CONFIDENCE

def main():
    print(f"Starting Prometheus exporter on port {EXPORTER_PORT}...")
    start_http_server(EXPORTER_PORT)
    print(f"Polling {APP_URL} every {POLL_INTERVAL}s")
    while True:
        confidence = fetch_confidence()
        CONFIDENCE_GAUGE.set(confidence)
        print(f"[INFO] prediction_confidence_score = {confidence:.4f}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
