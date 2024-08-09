import json

from compmatrix import db


# We used object here since the model type is _FSAModel, and we shouldn't
# use a private type.
def jsonify_model_object(model: object):
    print(model.__dict__)
