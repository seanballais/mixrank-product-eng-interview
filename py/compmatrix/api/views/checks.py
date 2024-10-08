from collections import OrderedDict

from werkzeug.datastructures import MultiDict

from compmatrix.api.views import queries, messages
from compmatrix.api.views.codes import AnomalyCode


def check_for_unknown_params(resp: dict[str, object | list],
                             known_params: list[str],
                             client_params: MultiDict[str, str]):
    # We need to preserve the order.
    unknown_params: list[str] = [
        k for k in client_params.keys() if k not in known_params
    ]
    if unknown_params:
        if 'errors' not in resp:
            resp['errors'] = []

        message: str = messages.create_unknown_params_message(unknown_params)
        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.UNRECOGNIZED_FIELD,
            'parameters': unknown_params
        })


def check_for_missing_params(resp: dict[str, object | list],
                             required_params: list[str],
                             client_params: MultiDict[str, str]):
    missing_params: list[str] = [
        p for p in required_params if p not in client_params.keys()
    ]
    if missing_params:
        if 'errors' not in resp:
            resp['errors'] = []

        missing_params_list: list[str] = sorted(list(missing_params))
        resp['errors'].append({
            'message': messages.create_missing_params_message(
                missing_params_list
            ),
            'code': AnomalyCode.MISSING_FIELD,
            'parameters': list(missing_params)
        })


def check_for_unknown_ids_in_params(resp: dict[str, object | list],
                                    params: OrderedDict[str, list[int] | int]):
    # We need the `params` parameters to be in order. Although insertion order
    # of dictionaries since Python 3.7 is preserved, we opted to use
    # OrderedDict here to properly communicate that we're expecting the
    # parameter to have its key-value pairs in a specific order.
    params_with_unknown_ids: list[str] = []
    unknown_ids_per_param: dict[str, list[int] | int] = {}
    for name, value in params.items():
        if type(value) is list:
            param_value = value
        else:
            param_value = [value]

        unknown_ids: list[int] = queries.get_unknown_ids_in_list(param_value)
        if unknown_ids:
            params_with_unknown_ids.append(name)
            unknown_ids_per_param[name] = unknown_ids

    if params_with_unknown_ids:
        if 'errors' not in resp:
            resp['errors'] = []

        num_unknown_ids: int = 0
        diagnostics: dict[str, list[int] | int] = {}
        for name, unknown_ids in unknown_ids_per_param.items():
            if type(params[name]) is list:
                # Makes sure that the diagnostics value is a list when the
                # parameter expected a list.
                num_unknown_ids += len(unknown_ids)
                diagnostics[name] = unknown_ids
            else:
                # Makes sure that the diagnostics value is just one item
                # when the parameter expected a non-iterable.
                num_unknown_ids += 1
                diagnostics[name] = unknown_ids[0]

        message: str = messages.create_unknown_ids_params_message(
            params_with_unknown_ids, num_unknown_ids)
        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.UNKNOWN_ID,
            'parameters': params_with_unknown_ids,
            'diagnostics': diagnostics
        })
