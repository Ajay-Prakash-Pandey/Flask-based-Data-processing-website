from flask import Blueprint, request, jsonify, send_file  # type: ignore
import io  # type: ignore
import pandas as pd  # type: ignore
from typing import Optional, Dict, Any  # type: ignore
from services.report_service import generate_csv_report, generate_json_report, generate_pdf_report, generate_ppt_report, generate_docx_report  # type: ignore

report_bp = Blueprint("report_bp", __name__)

@report_bp.route("/csv", methods=["POST"])
def download_csv():  # type: ignore
    try:
        data = request.json
        if not data or "cleaned_data" not in data:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(data["cleaned_data"])  # type: ignore
        filename = data.get("filename", "data.csv")
        
        content, export_filename = generate_csv_report(df, filename)
        
        if content is None:
            return jsonify({"error": "CSV generation failed"}), 400
        
        return send_file(
            io.BytesIO(content),
            mimetype="text/csv",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route("/json", methods=["POST"])
def download_json():  # type: ignore
    try:
        data = request.json
        if not data or "cleaned_data" not in data:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(data["cleaned_data"])  # type: ignore
        filename = data.get("filename", "data.csv")
        
        content, export_filename = generate_json_report(df, filename)
        
        if content is None:
            return jsonify({"error": "JSON generation failed"}), 400
        
        return send_file(
            io.BytesIO(content),
            mimetype="application/json",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route("/pdf", methods=["POST"])
def download_pdf():  # type: ignore
    try:
        data = request.json
        if not data or "cleaned_data" not in data:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(data["cleaned_data"])  # type: ignore
        filename = data.get("filename", "data.csv")
        stats: Optional[Dict[str, Any]] = data.get("statistics")
        
        content, export_filename = generate_pdf_report(df, filename, stats)
        
        if content is None:
            return jsonify({"error": "PDF generation not available. Install reportlab: pip install reportlab"}), 400
        
        return send_file(
            io.BytesIO(content),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route("/pptx", methods=["POST"])
def download_pptx():  # type: ignore
    try:
        data = request.json
        if not data or "cleaned_data" not in data:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(data["cleaned_data"])  # type: ignore
        filename = data.get("filename", "data.csv")
        stats: Optional[Dict[str, Any]] = data.get("statistics")
        
        content, export_filename = generate_ppt_report(df, filename, stats)
        
        if content is None:
            return jsonify({"error": "PowerPoint generation not available. Install python-pptx: pip install python-pptx"}), 400
        
        return send_file(
            io.BytesIO(content),
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route("/docx", methods=["POST"])
def download_docx():  # type: ignore
    try:
        data = request.json
        if not data or "cleaned_data" not in data:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(data["cleaned_data"])  # type: ignore
        filename = data.get("filename", "data.csv")
        stats: Optional[Dict[str, Any]] = data.get("statistics")
        
        content, export_filename = generate_docx_report(df, filename, stats)
        
        if content is None:
            return jsonify({"error": "Word generation not available. Install python-docx: pip install python-docx"}), 400
        
        return send_file(
            io.BytesIO(content),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
