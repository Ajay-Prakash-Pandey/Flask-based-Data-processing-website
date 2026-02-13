from flask import Blueprint, request, jsonify
from services.ml_service import make_prediction

ml_bp = Blueprint("ml_bp", __name__)

@ml_bp.route("/predict", methods=["POST"])
def predict_api():
    data = request.get_json(silent=True) or {}
    features = data.get("features")

    if not isinstance(features, list) or not features:
        return jsonify({"error": "features must be a non-empty list"}), 400

    result = make_prediction(features)
    return jsonify({"prediction": int(result)})
