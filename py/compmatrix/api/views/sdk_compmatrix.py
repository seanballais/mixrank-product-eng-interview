from http import HTTPStatus

from flask import request

from compmatrix.api.views.codes import AnomalyCode


def numbers():
    # SQ: Query to base things off of.
    # SELECT app_id
    # FROM app_sdk
    # WHERE
    #   (sdk_id = 33 AND installed = false) OR
    #   (sdk_id = 875 AND installed = true)
    # GROUP BY app_id
    # HAVING COUNT(sdk_id) = 2
    # ORDER BY app_id
    #
    #             ID
    # ---------------
    # PayPal   |   33
    # Stripe   |  875
    # Braintree| 2081
    #
    # We're sending back an HTTP 422 when responding to requests with
    # incomplete parameters, since everything is alright, but we're missing
    # some required content, which makes us unable to process stuff. Besides,
    # HTTP 422 is already a part of HTTP since RFC 9110
    # (https://datatracker.ietf.org/doc/html/rfc9110), which was published on
    # June 2022, so no worries about non-standard practices.
    if 'from_sdks' not in request.args and 'to_sdks' not in request.args:
        return {
            'error': {
                'message': 'Required parameters, from_sdks and to_sdks, '
                           'are missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'from_sdks',
                    'to_sdks'
                ]
            }
        }, HTTPStatus.UNPROCESSABLE_ENTITY

    if 'from_sdks' not in request.args:
        return {
            'error': {
                'message': 'Required parameter, from_sdks, is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['from_sdks']
            }
        }, HTTPStatus.UNPROCESSABLE_ENTITY

    if 'to_sdks' not in request.args:
        return {
            'error': {
                'message': 'Required parameter, to_sdks, is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            }
        }, HTTPStatus.UNPROCESSABLE_ENTITY

    from_sdks_param: list = request.args.getlist('from_sdks')
    to_sdks_param: list = request.args.getlist('to_sdks')

    resp: dict[str, object] = {
        'data': {
            'numbers': [
                [4, 3, 3],
                [2, 5, 3],
                [3, 3, 4]
            ]
        }
    }

    other_params: list[str] = [
        k for k in request.args.keys() if k != 'from_sdks' and k != 'to_sdks'
    ]
    if other_params:
        params_substr: str = ', '.join([f'"{p}"' for p in other_params[:-1]])
        params_substr += f', and "{other_params[-1]}"'
        warning_msg: str = f'Unrecognized parameters, {params_substr}.'
        resp['warning'] = {
            'message': warning_msg,
            'code': AnomalyCode.UNRECOGNIZED_FIELD,
            'fields': other_params
        }

    return resp


def apps():
    pass
