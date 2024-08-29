from http import HTTPStatus

from compmatrix.api.views.codes import AnomalyCode

from .constants import SDK_COMPMATRIX_APPS_ENDPOINT


# Tests to ensure that the `other_from_sdks` and `other_to_sdks` parameters are
# only specified when the `from_sdk` and `to_sdk` parameters are not specified
# or are empty strings.
def test_has_other_from_sdks_and_from_sdk(client, sdk_ids):
    count = 2
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': [sdk_ids[0]],
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': [sdk_ids[1]],
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "other_from_sdks" and '
                           '"other_to_sdks", must only be specified if the '
                           '"from_sdk" and "to_sdk" parameters are '
                           'unspecified.',
                'code': AnomalyCode.MISUSED_PARAMETER,
                'parameters': [
                    'other_from_sdks',
                    'other_to_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
