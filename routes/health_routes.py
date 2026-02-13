from flask import Blueprint, jsonify

health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/")
def health():
    return jsonify({"status": "OK", "message": "Flask ML System Running"})
