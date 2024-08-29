from dataclasses import dataclass
import typing


@dataclass
class ModelEncoderFilter:
    target_fields: list[str] | str
    filter_func: typing.Callable[[typing.Any], typing.Any]


# We used object here since the model type is _FSAModel, and we shouldn't
# use a private type.
def encode_model_as_dict(
        model_obj: object, ignored_fields: list[str] = None,
        filters: list[ModelEncoderFilter] = None
) -> dict[str, object]:
    """
    Encodes a model as a dictionary. We can ignore fields, as well as, apply
    filters to each field as needed.

    :param model_obj: The model object we will be converting to a dictionary.
    :param ignored_fields: The fields to ignore.
    :param filters: The filters that will be applied to specific fields. If
                    multiple filters act on a field, only the last filter
                    defined will be used. There is no need to chain together
                    multiple filters for one field, at this moment. Filter
                    functions are expected to accept only one argument.
    :return: A dictionary version of the model object.
    """
    ignored_fields_set: set[str] = {'_sa_instance_state'}
    if ignored_fields:
        ignored_fields_set.update(ignored_fields)

    field_to_filter: dict[str, typing.Callable[[object], object]] = {}
    if filters:
        for f in filters:
            target_fields: list[str] = []

            # We're not expecting to be passed an iterable, so we can just
            # check if it is a list or a string.
            if type(f.target_fields) is list:
                target_fields = f.target_fields
            else:
                target_fields.append(f.target_fields)

            for field in target_fields:
                field_to_filter[field] = f.filter_func

    model_obj_dict: dict[str, object] = {}
    for k, v in model_obj.__dict__.items():
        if k not in ignored_fields_set:
            if k in field_to_filter:
                model_obj_dict[k] = field_to_filter[k](v)
            else:
                model_obj_dict[k] = v

    return model_obj_dict
