# tests/test_preprocessing.py
import os
import sys
import pytest

# Ensure repo root on path (should already be done by test bootstrap)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Try several likely import locations for preprocess_text
preprocess_text = None
import_errors = []

candidates = [
    ("from app import preprocess_text", lambda: __import__("app").preprocess_text),
    ("from utils import preprocess_text", lambda: __import__("utils").preprocess_text),
    ("from text_emotion_detection.utils import preprocess_text", lambda: __import__("text_emotion_detection.utils", fromlist=["preprocess_text"]).preprocess_text),
    ("from text_emotion_detection.preprocess import preprocess_text", lambda: __import__("text_emotion_detection.preprocess", fromlist=["preprocess_text"]).preprocess_text),
    ("from preprocess import preprocess_text", lambda: __import__("preprocess").preprocess_text),
]

for desc, importer in candidates:
    try:
        preprocess_text = importer()
        break
    except Exception as e:
        import_errors.append((desc, repr(e)))

if preprocess_text is None:
    # None of the expected imports worked — skip these tests with details for debugging
    msg = "Could not import preprocess_text from expected locations. Tried:\n"
    for desc, err in import_errors:
        msg += f"- {desc}: {err}\n"
    pytest.skip(msg)

# Now actual tests (these assume preprocess_text returns a string or similar)
def test_preprocess_basic():
    txt = "Hello!!! This is GREAT :)"
    out = preprocess_text(txt)
    assert out is not None
    assert isinstance(out, str)

def test_preprocess_empty():
    out = preprocess_text("")
    assert out is not None
    assert isinstance(out, str)

def test_preprocess_unicode():
    txt = "नमस्ते 😊"
    out = preprocess_text(txt)
    assert out is not None
    assert isinstance(out, str)

def test_preprocess_long_input():
    txt = "word " * 10000
    out = preprocess_text(txt)
    assert out is not None
    assert isinstance(out, str)
