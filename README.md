# Flask-based Data Processing Website

A Flask web application for uploading datasets, cleaning and analyzing data, visualizing insights, running machine learning predictions, and exporting reports in multiple formats.

## Project Description

This project helps users process tabular data quickly through a web interface and API endpoints.  
It supports end-to-end data workflows:

- Upload datasets (`.csv`, `.json`, `.xlsx`, `.xls`, `.tsv`, `.txt`, `.parquet`, `.hdf5`, `.feather`)
- Automatic data cleaning (missing values, duplicates, type-aware handling)
- Summary analytics and visualizations (distribution and correlation views)
- ML prediction endpoint for model-based inference
- Export cleaned data and reports as `CSV`, `JSON`, `XLSX`, `PDF`, `PPTX`, and `DOCX`

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Pandas / NumPy
- Matplotlib / Seaborn
- ReportLab / python-pptx / python-docx

## Run Locally

```bash
pip install -r requirements.txt
python run.py
```

Open in browser: `http://127.0.0.1:5000`

## Deploy on Render (Free Plan)

This repo is now deployment-ready for Render with `render.yaml`.

1. Push your code to GitHub.
2. Go to Render and create a new `Blueprint` service from your repo.
3. Render will auto-detect `render.yaml` and create the web service.
4. After deploy, open:
   - App URL: `https://<your-service>.onrender.com`
   - Health check: `https://<your-service>.onrender.com/api/health/`

### Manual Render Setup (without Blueprint)

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn run:app`
- Environment variables:
  - `SECRET_KEY` = any long random string
  - `DATABASE_URL` = `sqlite:///data.db` (or Render Postgres URL if you upgrade)

## Alternative Free Platform: Railway

1. Create a new project from your GitHub repo.
2. Set the start command to `gunicorn run:app`.
3. Add env vars:
   - `SECRET_KEY` = any long random string
   - `DATABASE_URL` = `sqlite:///data.db` (or Railway Postgres URL)

Note: Free tiers usually sleep after inactivity and local disk can be ephemeral.  
For persistent production data, use a managed Postgres instance.

## Main API Routes

- `/api/data/*` - upload and clean data
- `/api/analytics/*` - statistics and charts
- `/api/ml/predict` - prediction endpoint
- `/api/report/*` and `/api/export/*` - report/data exports

## GitHub About

Flask web app for dataset cleaning, analysis, ML prediction, and multi-format report export.

## Repository Tags

`flask`, `python`, `data-processing`, `data-cleaning`, `data-analysis`, `machine-learning`, `pandas`, `data-visualization`, `reporting`, `api`
