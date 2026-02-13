from flask import Blueprint, request, jsonify, send_file
import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from services.report_service import (
    generate_csv_report,
    generate_json_report,
    generate_xlsx_report,
    generate_pdf_report,
    generate_ppt_report,
    generate_docx_report
)

export_bp = Blueprint("export_bp", __name__)

@export_bp.route("/cleaned-csv", methods=["POST"])
def export_cleaned_csv():
    """Export cleaned data as CSV"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)  # type: ignore
        
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        export_filename = f"{filename.replace('.csv', '')}_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            csv_buffer,
            mimetype="text/csv",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/report-pdf", methods=["POST"])
def export_report_pdf():
    """Export complete report as PDF"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        stats = data.get("statistics", {})
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)  # type: ignore
        pdf_bytes, export_filename = generate_pdf_report(df, filename, stats)
        
        if pdf_bytes is None:
            return jsonify({"error": "Failed to generate PDF report"}), 500
        
        pdf_buffer = io.BytesIO(pdf_bytes)
        
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=export_filename
        )
    except ImportError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/report-pptx", methods=["POST"])
def export_report_pptx():
    """Export complete report as PowerPoint"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        stats = data.get("statistics", {})
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)
        ppt_bytes, export_filename = generate_ppt_report(df, filename, stats)
        
        if ppt_bytes is None:
            return jsonify({"error": "Failed to generate PowerPoint report"}), 500
        
        ppt_buffer = io.BytesIO(ppt_bytes)
        
        return send_file(
            ppt_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name=export_filename
        )
    except ImportError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/report-docx", methods=["POST"])
def export_report_docx():
    """Export complete report as Word document"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        stats = data.get("statistics", {})
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)
        docx_bytes, export_filename = generate_docx_report(df, filename, stats)
        
        if docx_bytes is None:
            return jsonify({"error": "Failed to generate Word document"}), 500
        
        docx_buffer = io.BytesIO(docx_bytes)
        
        return send_file(
            docx_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=export_filename
        )
    except ImportError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/report-all", methods=["POST"])
def export_all_reports():
    """Generate all report formats at once"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        stats = data.get("statistics", {})
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)  # type: ignore
        
        results: Dict[str, Any] = {
            "csv": None,
            "xlsx": None,
            "json": None,
            "pdf": None,
            "pptx": None,
            "docx": None,
            "errors": []
        }
        
        # Generate CSV
        try:
            csv_bytes, csv_name = generate_csv_report(df, filename)
            results["csv"] = csv_name if csv_bytes else None
        except Exception as e:
            results["errors"].append(f"CSV: {str(e)}")  # type: ignore
        
        # Generate XLSX
        try:
            xlsx_bytes, xlsx_name = generate_xlsx_report(df, filename, stats)
            results["xlsx"] = xlsx_name if xlsx_bytes else None
        except Exception as e:
            results["errors"].append(f"XLSX: {str(e)}")  # type: ignore
        
        # Generate JSON
        try:
            json_bytes, json_name = generate_json_report(df, filename)
            results["json"] = json_name if json_bytes else None
        except Exception as e:
            results["errors"].append(f"JSON: {str(e)}")  # type: ignore
        
        # Generate PDF
        try:
            pdf_bytes, pdf_name = generate_pdf_report(df, filename, stats)
            results["pdf"] = pdf_name if pdf_bytes else None
        except Exception as e:
            results["errors"].append(f"PDF: {str(e)}")  # type: ignore
        
        # Generate PowerPoint
        try:
            ppt_bytes, ppt_name = generate_ppt_report(df, filename, stats)
            results["pptx"] = ppt_name if ppt_bytes else None
        except Exception as e:
            results["errors"].append(f"PowerPoint: {str(e)}")  # type: ignore
        
        # Generate DOCX
        try:
            docx_bytes, docx_name = generate_docx_report(df, filename, stats)
            results["docx"] = docx_name if docx_bytes else None
        except Exception as e:
            results["errors"].append(f"Word: {str(e)}")  # type: ignore
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/cleaned-xlsx", methods=["POST"])
def export_cleaned_xlsx():
    """Export cleaned data as Excel"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)  # type: ignore
        
        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:  # type: ignore
            df.to_excel(writer, sheet_name='Cleaned Data', index=False)  # type: ignore
        
        xlsx_buffer.seek(0)
        
        export_filename = f"{filename.replace('.csv', '')}_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            xlsx_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=export_filename
        )
    except ImportError:
        return jsonify({"error": "Excel export requires openpyxl. Install with: pip install openpyxl"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/cleaned-json", methods=["POST"])
def export_cleaned_json():
    """Export cleaned data as JSON"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid request data"}), 400
        
        cleaned_df_json = data.get("cleaned_data")
        filename = data.get("filename", "cleaned_data")
        
        if not cleaned_df_json:
            return jsonify({"error": "No cleaned data provided"}), 400
        
        df = pd.read_json(cleaned_df_json)  # type: ignore
        
        json_buffer = io.BytesIO()
        json_buffer.write(df.to_json(orient='records', indent=2).encode())  # type: ignore
        json_buffer.seek(0)
        
        export_filename = f"{filename.replace('.csv', '')}_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            json_buffer,
            mimetype="application/json",
            as_attachment=True,
            download_name=export_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
