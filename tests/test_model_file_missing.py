import os
import pytest
import app

def test_model_file_missing(monkeypatch, tmp_path):
    # simulate missing model path: monkeypatch the model load path/func to raise
    def fake_load():
        raise FileNotFoundError("model file not found")
    monkeypatch.setattr(app, 'load_model', fake_load)
    with pytest.raises(FileNotFoundError):
        app.load_model()
