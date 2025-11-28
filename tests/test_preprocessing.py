import pytest

# adjust import path to where your preprocess function lives
from app import preprocess_text

def test_preprocess_basic():
    txt = "Hello!!! This is GREAT :)"
    out = preprocess_text(txt)
    assert isinstance(out, str)
    assert "hello" in out.lower() or len(out) > 0

def test_preprocess_empty():
    assert preprocess_text("") in ("", None) or isinstance(preprocess_text(""), str)

def test_preprocess_unicode():
    txt = "नमस्ते 😊"
    out = preprocess_text(txt)
    assert out is not None
    assert isinstance(out, str)

def test_preprocess_long_input():
    txt = "word " * 10000
    out = preprocess_text(txt)
    assert isinstance(out, str)
    assert len(out) > 0
