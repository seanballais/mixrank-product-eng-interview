from compmatrix.api.views import messages
from compmatrix.api.views.codes import AnomalyCode


def generate_wrong_valued_params_resp_error(resp: dict[str, object | list],
                                            params: list[str]):
    # TODO: Add diagnostics field here, but not for now, due to time
    #       constraints.
    if 'errors' not in resp:
        resp['errors'] = []

    resp['errors'].append({
        'message': messages.create_wrong_valued_params_message(params),
        'code': AnomalyCode.INVALID_PARAMETER_VALUE,
        'parameters': params
    })
