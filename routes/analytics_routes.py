from flask import Blueprint, request, jsonify
from services.visualization_service import (
    generate_column_distribution_chart,
    generate_correlation_heatmap,
    generate_summary_statistics
)
import pandas as pd

analytics_bp = Blueprint("analytics_bp", __name__)

@analytics_bp.route("/summary", methods=["POST"])
def get_summary():
    """Get comprehensive data summary with statistics"""
    try:
        file = request.files.get("file")
        if not file or not file.filename or not file.filename.endswith('.csv'):
            return jsonify({"error": "Please upload a CSV file"}), 400
        
        encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
        df = None
        for encoding in encodings:
            try:
                file.stream.seek(0)
                df = pd.read_csv(file.stream, encoding=encoding)  # type: ignore
                break
            except (UnicodeDecodeError, UnicodeError, LookupError):
                continue
        if df is None:
            file.stream.seek(0)
            df = pd.read_csv(file.stream, encoding='utf-8', errors='replace')  # type: ignore
        
        stats = generate_summary_statistics(df)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/distribution", methods=["POST"])
def get_distribution_chart():
    """Generate distribution chart for a specific column"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        file_data = data.get("file_data")
        column = data.get("column")
        
        if not file_data or not column:
            return jsonify({"error": "Missing file_data or column"}), 400
        
        df = pd.read_json(file_data)
        chart_img = generate_column_distribution_chart(df, column)
        
        if chart_img is None:
            return jsonify({"error": "Could not generate chart"}), 500
        
        return jsonify({"chart": chart_img})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/correlation", methods=["POST"])
def get_correlation():
    """Generate correlation heatmap"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        file_data = data.get("file_data")
        
        if not file_data:
            return jsonify({"error": "Missing file_data"}), 400
        
        df = pd.read_json(file_data)
        chart_img = generate_correlation_heatmap(df)
        
        if chart_img is None:
            return jsonify({"error": "Insufficient data for correlation"}), 400
        
        return jsonify({"chart": chart_img})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
