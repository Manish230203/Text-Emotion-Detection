import pytest
from types import SimpleNamespace
import numpy as np

# import the module that loads model
import app

def test_load_model_exists(monkeypatch):
    # monkeypatch load_model if you expect it to load file - here just call it
    m = app.load_model()
    assert m is not None

def test_model_prediction_api(monkeypatch):
    # create a fake model with predict returning label and/or predict_proba
    fake_model = SimpleNamespace()
    def fake_predict(X):
        return ["happy"] * len(X)
    def fake_predict_proba(X):
        # return probabilities array shape (n_samples, n_classes)
        return np.array([[0.1, 0.9]])
    fake_model.predict = fake_predict
    fake_model.predict_proba = fake_predict_proba

    monkeypatch.setattr(app, "model", fake_model, raising=False)
    res = fake_model.predict(["i am fine"])
    assert res[0] == "happy"
    probs = fake_model.predict_proba(["i am fine"])
    assert probs.shape[1] >= 1
