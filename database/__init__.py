# from flask import Flask
# from core_app.config import Config
# from core_app.database.db import init_db

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     init_db(app)

#     from core_app.routes.data_routes import data_bp
#     from core_app.routes.ml_routes import ml_bp
#     from core_app.routes.health_routes import health_bp

#     app.register_blueprint(data_bp, url_prefix="/api/data")
#     app.register_blueprint(ml_bp, url_prefix="/api/ml")
#     app.register_blueprint(health_bp, url_prefix="/api/health")

#     return app
