from collections import OrderedDict

from compmatrix.api.views import queries, messages
from compmatrix.api.views.codes import AnomalyCode


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
