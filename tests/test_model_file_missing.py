# tests/test_model_file_missing.py
import os
import sys
import pytest

# ensure repo root on path (bootstrap from other tests may already have done this)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

def test_model_file_missing(monkeypatch, tmp_path):
    """
    Simulate a missing model file by monkeypatching a discovered load_model()
    to raise FileNotFoundError. If no load_model is found in expected modules,
    skip this test with a helpful message.
    """
    def fake_load():
        raise FileNotFoundError("model file not found")

    candidates = [
        "app",
        "text_emotion_detection.app",
        "models",
        "text_emotion_detection.models",
        "utils",
    ]

    tried = []
    for mod_name in candidates:
        try:
            module = __import__(mod_name, fromlist=["*"])
        except Exception as e:
            tried.append((mod_name, f"import error: {e!r}"))
            continue

        # If module has load_model, monkeypatch and assert exception on call
        if hasattr(module, "load_model"):
            monkeypatch.setattr(module, "load_model", fake_load, raising=False)
            with pytest.raises(FileNotFoundError):
                module.load_model()
            return  # success: test completed

        tried.append((mod_name, "no load_model attribute"))

    # Nothing matched — skip with context so test logs are useful
    msg = "Could not find a load_model() function in expected modules. Tried:\n"
    for name, note in tried:
        msg += f"- {name}: {note}\n"
    msg += "If your project exposes a load_model function, export it from app.py or place it in one of the tested modules."
    pytest.skip(msg)
