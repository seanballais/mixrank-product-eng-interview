from compmatrix import model_encoders
from compmatrix.api import models


def index():
    sdks = models.SDK.query.order_by(models.SDK.name.asc())

    cleaned_sdks: list[dict[str, object]] = []
    for sdk in sdks:
        cleaned_sdks.append(model_encoders.encode_model_as_dict(sdk))

    return {
        'sdks': cleaned_sdks
    }
