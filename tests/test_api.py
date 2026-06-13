import os
import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert "model_version" in data

def test_predict_returns_label_and_confidence():
    payload = {"text": "This is a great product!"}
    response = requests.post(f"{BASE_URL}/predict", json=payload,
                             headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert data["label"] in ["POSITIVE", "NEGATIVE"]
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 1
    assert "model_version" in data

def test_predict_negative_text():
    payload = {"text": "This is terrible, I hate it. Awful experience."}
    response = requests.post(f"{BASE_URL}/predict", json=payload,
                             headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert data["label"] in ["POSITIVE", "NEGATIVE"]

def test_health_returns_model_version_unstable():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert data["model_version"] == "unstable-v1"
