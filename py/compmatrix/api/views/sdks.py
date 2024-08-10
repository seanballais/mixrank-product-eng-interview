from compmatrix import model_encoders
from compmatrix.api import models


def index():
    sdks = models.SDK.query.all()

    cleaned_sdks: list[dict[str, object]] = []
    for sdk in sdks:
        cleaned_sdks.append(model_encoders.clean_model_object_dict(sdk))

    return {
        'sdks': cleaned_sdks
    }
