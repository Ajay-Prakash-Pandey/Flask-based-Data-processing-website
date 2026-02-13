import os
from typing import Any, List, Union

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model: Any = None

if os.path.exists(MODEL_PATH):
    try:
        import joblib  # type: ignore
        model = joblib.load(MODEL_PATH)  # type: ignore
    except Exception:
        model = None

def predict(features: List[Union[int, float]]) -> float:
    if model is None:
        return 0.0
    try:
        return float(model.predict([features])[0])
    except Exception:
        return 0.0
