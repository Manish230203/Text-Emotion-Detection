# tests/test_app.py (top)
import os, sys

# compute absolute path to project folder (works whether folder name has spaces)
proj_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Text Emotion Detection"))
# if you later rename folder to text_emotion_detection, change the line above to:
# proj_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "text_emotion_detection"))

# add project folder to import path
sys.path.insert(0, proj_folder)

import json
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_health_endpoint(client):
    # adjust if your app has root or /health
    rv = client.get('/')
    assert rv.status_code in (200, 404)  # if root returns 200, else test /health
    # if known response check: assert b'OK' in rv.data

def test_predict_valid(client, monkeypatch):
    # monkeypatch model to deterministic response
    class FakeModel:
        def predict(self, X): return ["sad"]
        def predict_proba(self, X): return [[0.8]]
    monkeypatch.setattr('app.model', FakeModel(), raising=False)

    payload = {"text": "I am feeling terrible today"}
    rv = client.post('/predict', json=payload)
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'emotion' in data or 'pred' in data
    # if you return score:
    if 'score' in data:
        assert 0.0 <= data['score'] <= 1.0

def test_predict_missing_payload(client):
    rv = client.post('/predict', data='{}', content_type='application/json')
    # expecting 400 or 422 depending on implementation
    assert rv.status_code in (400, 422)

def test_predict_invalid_type(client):
    rv = client.post('/predict', json={"text": 12345})
    assert rv.status_code in (400, 422)
