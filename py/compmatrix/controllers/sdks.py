from compmatrix import models


def index():
    sdks = models.SDK.query.all()
    for sdk in sdks:
        models.encoders.jsonify_model_object(sdk)
