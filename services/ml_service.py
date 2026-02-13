from ml.model import predict
from database.models import Prediction
from database.db import db

def make_prediction(features):
    result = predict(features)

    record = Prediction(
        input_features=str(features),
        prediction_result=str(result)
    )
    db.session.add(record)
    db.session.commit()

    return result
