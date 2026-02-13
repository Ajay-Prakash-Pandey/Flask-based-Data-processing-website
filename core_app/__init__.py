from flask import Flask, render_template
from typing import Any
from .config import Config
from database.db import init_db

def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    init_db(app)
    
    @app.route("/")
    def index() -> Any:
        return render_template("index.html")
    
    @app.route("/result")
    def result() -> Any:
        return render_template("result.html")
    
    @app.route("/dashboard")
    def dashboard() -> Any:
        return render_template("dashboard.html")
    
    from routes.data_routes import data_bp
    from routes.ml_routes import ml_bp
    from routes.health_routes import health_bp
    from routes.report_routes import report_bp
    from routes.analytics_routes import analytics_bp
    from routes.export_routes import export_bp
    
    app.register_blueprint(data_bp, url_prefix="/api/data")
    app.register_blueprint(ml_bp, url_prefix="/api/ml")
    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(report_bp, url_prefix="/api/report")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(export_bp, url_prefix="/api/export")
    
    return app
