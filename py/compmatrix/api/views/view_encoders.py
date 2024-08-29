from compmatrix import model_encoders
from compmatrix.api import models
from compmatrix.api.views.filters import date_filter


def encode_app_model_object(app_obj: models.App) -> dict[str, object]:
    ignored_fields = ['sdks']
    filters = [
        model_encoders.ModelEncoderFilter('release_date', date_filter)
    ]
    return model_encoders.encode_model_as_dict(app_obj, ignored_fields,
                                               filters)
