import json
import pprint

from compmatrix import db


# We used object here since the model type is _FSAModel, and we shouldn't
# use a private type.
def clean_model_object_dict(model: object) -> dict[str, object]:
    return {
        k: v for k, v in model.__dict__.items() if k != '_sa_instance_state'
    }
