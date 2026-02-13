from flask import Blueprint, request, jsonify, send_file
import io
import pandas as pd
from services.data_service import process_file, detect_file_format

data_bp = Blueprint("data_bp", __name__)

ALLOWED_FORMATS = {'csv', 'json', 'xlsx', 'xls', 'tsv', 'txt', 'parquet', 'pq', 'hdf5', 'h5', 'feather'}

@data_bp.route("/upload", methods=["POST"])
def upload_data():
    """Upload and process data file - supports multiple formats"""
    file = request.files.get("file")
    
    if not file or not file.filename:
        return jsonify({"error": "No file provided"}), 400
    
    # Check file format
    file_format = detect_file_format(file.filename)
    if file_format == 'unknown':
        return jsonify({
            "error": f"Unsupported file format. Supported: {', '.join(sorted(ALLOWED_FORMATS))}"
        }), 400
    
    try:
        result, df_cleaned = process_file(file)
        
        # Store cleaned dataframe for download
        csv_buffer = io.BytesIO()
        df_cleaned.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Store in session-like format
        result["cleaned_data_available"] = True
        result["filename_cleaned"] = f"cleaned_{file.filename}"
        result["supported_formats"] = list(ALLOWED_FORMATS)
        
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@data_bp.route("/download-cleaned", methods=["POST"])
def download_cleaned_data():
    """Download the cleaned CSV file"""
    try:
        data = request.json
        
        if not data or "cleaned_data" not in data:
            return jsonify({"error": "No cleaned data available"}), 400
        
        df = pd.read_json(data["cleaned_data"])  # type: ignore
        
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        filename = f"cleaned_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            csv_buffer,
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@data_bp.route("/supported-formats", methods=["GET"])
def get_supported_formats():
    """Get list of supported file formats"""
    return jsonify({
        "supported_formats": sorted(list(ALLOWED_FORMATS)),
        "formats_description": {
            "csv": "Comma Separated Values - Plain text tabular data",
            "json": "JavaScript Object Notation - Structured data format",
            "xlsx": "Excel 2007+ Workbook - Microsoft Excel format",
            "xls": "Excel 97-2003 Workbook - Legacy Excel format",
            "tsv": "Tab Separated Values - Tab-delimited text",
            "txt": "Plain text file with auto-delimiter detection",
            "parquet": "Apache Parquet - Columnar storage format",
            "hdf5": "HDF5 - Hierarchical data format",
            "feather": "Apache Feather - Fast serialization format"
        }
    })
