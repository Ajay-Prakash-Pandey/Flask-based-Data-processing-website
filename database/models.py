from datetime import datetime, timezone
from database.db import db

class UploadedDataset(db.Model):  # type: ignore
    """Model for storing uploaded dataset metadata."""
    __tablename__ = "uploaded_datasets"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    rows = db.Column(db.Integer)
    columns = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Prediction(db.Model):  # type: ignore
    """Model for storing ML prediction results."""
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    input_features = db.Column(db.String(255))
    prediction_result = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
