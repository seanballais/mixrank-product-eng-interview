from http import HTTPStatus

from compmatrix.api.views.codes import AnomalyCode
from compmatrix.tests.api.views.test_sdk_compmatrix import (
    BASE_SDK_COMPMATRIX_ENDPOINT
)

from . import query_utils

SDK_COMPMATRIX_APPS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/apps'


def test_from_sdk_non_integer(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': '🥹 Doom Crossing: Eternal Horizons 🤬',
        'to_sdk': sdk_ids[0],
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdk", has an invalid value. It '
                           'must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdk'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_to_sdk_non_integer(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': 'Tell me how am I supposed to live without youuuuuuu',
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdk", has an invalid value. It '
                           'must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdk'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_other_from_sdks_non_integer(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'other_from_sdks': 'Memories follow meee left and riiiiighhht',
        'to_sdk': sdk_ids[0],
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_from_sdks", has an invalid '
                           'value. It must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_from_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_other_from_sdks_non_integer2(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'other_from_sdks': [
            'What is Love?',
            'Baby, don\'t hurt me',
            'Baby, don\'t hurt me',
            'No mooorrreee'
        ],
        'to_sdk': sdk_ids[0],
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_from_sdks", has an invalid '
                           'value. It must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_from_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_other_from_sdks_non_integer3(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'other_from_sdks': [
            'Do you think time would pass me by',
            'Cause you know I\'d walk a',
            1000,
            '1000',
            'miles',
            'If I could just see you tonight'
        ],
        'to_sdk': sdk_ids[0],
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_from_sdks", has an invalid '
                           'value. It must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_from_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_other_to_sdks_non_integer(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': 'Memories follow meee left and riiiiighhht',
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_to_sdks", has an invalid '
                           'value. It must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_to_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_other_to_sdks_non_integer2(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [
            'What is Love?',
            'Baby, don\'t hurt me',
            'Baby, don\'t hurt me',
            'No mooorrreee'
        ],
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_to_sdks", has an invalid value. '
                           'It must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_to_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_other_to_sdks_non_integer3(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [
            'Do you think time would pass me by',
            'Cause you know I\'d walk a',
            1000,
            '1000',
            'miles',
            'If I could just see you tonight'
        ],
        'count': 2,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_to_sdks", has an invalid '
                           'value. It must be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_to_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_count_non_integer(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': 'Take a moment to think of just flexibility, love, and trust',
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "count", has an invalid value. It must '
                           'be an integer.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'count'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_cursor_wrong_format(client, apps, sdk_ids):
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': 3,
        'cursor': 'verydemure.verycutesy',
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "cursor", has an invalid value. The '
                           'correct format is "<app name>;<app seller name>".',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'cursor'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_direction_invalid_value(client, apps, sdk_ids):
    cursor = query_utils.create_cursor_from_app_obj(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': 3,
        'cursor': cursor,
        'direction': 'spooky scary skeletooonnns'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "direction", has an invalid value. It '
                           'must only be either "previous" or "next".',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'direction'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_all_params(client, apps, sdk_ids):
    query_string = {
        'from_sdk': 'Maia hiii',
        'to_sdk': 'Maia hooooo',
        'count': 'Maia haaaa',
        'cursor': 'Maia hahaaa',
        'direction': 'Maia hiiiiiii'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdk", "to_sdk", "count", '
                           '"cursor", and "direction", have invalid values. '
                           'Values of "from_sdk", "to_sdk", and "count" must '
                           'be integers. The correct format for the value of '
                           '"cursor" is "<app name>;<app seller name>". The '
                           'value of "direction" must only be either '
                           '"previous" or "next".',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdk',
                    'to_sdk',
                    'count',
                    'cursor',
                    'direction'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_all_params2(client, apps, sdk_ids):
    query_string = {
        'other_from_sdks': 'Maia hiii',
        'other_to_sdks': 'Maia hooooo',
        'count': 'Maia haaaa',
        'cursor': 'Maia hahaaa',
        'direction': 'Maia hiiiiiii'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "other_from_sdks", "other_to_sdks", '
                           '"count", "cursor", and "direction", have invalid '
                           'values. Values of "other_from_sdks", '
                           '"other_to_sdks", and "count" must be integers. '
                           'The correct format for the value of "cursor" is '
                           '"<app name>;<app seller name>". The value of '
                           '"direction" must only be either "previous" or '
                           '"next".',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'other_from_sdks',
                    'other_to_sdks',
                    'count',
                    'cursor',
                    'direction'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_all_params3(client, apps, sdk_ids):
    query_string = {
        'from_sdk': 'Maia hiii',
        'other_from_sdks': 'Maia hiii',
        'to_sdk': 'Maia hooooo',
        'other_to_sdks': 'Maia hooooo',
        'count': 'Maia haaaa',
        'cursor': 'Maia hahaaa',
        'direction': 'Maia hiiiiiii'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdk", "other_from_sdks", '
                           '"to_sdk", "other_to_sdks", "count", "cursor", and '
                           '"direction", have invalid values. Values of '
                           '"from_sdk", "other_from_sdks", "to_sdk", '
                           '"other_to_sdks", and "count" must be integers. '
                           'The correct format for the value of "cursor" is '
                           '"<app name>;<app seller name>". The value of '
                           '"direction" must only be either "previous" or '
                           '"next".',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdk',
                    'other_from_sdks',
                    'to_sdk',
                    'other_to_sdks',
                    'count',
                    'cursor',
                    'direction'
                ]
            },
            {
                'message': 'Parameters, "other_from_sdks" and '
                           '"other_to_sdks", must only be specified if the '
                           '"from_sdk" and "to_sdk" parameters are '
                           'unspecified, respectively.',
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


def test_invalid_all_params4(client, apps, sdk_ids):
    query_string = {
        'from_sdk': 'Maia hiii',
        'other_from_sdks': 'Maia hiii',
        'to_sdk': 'Maia hooooo',
        'other_to_sdks': 'Maia hooooo',
        'count': 'Maia haaaa',
        'cursor': 'Maia hahaaa'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "direction", is missing. It '
                           'is required when the "cursor" parameter has a '
                           'value.',
                'code': AnomalyCode.MISSING_FIELD,
                'parameters': [
                    'direction'
                ],
            },
            {
                'message': 'Parameters, "from_sdk", "other_from_sdks", '
                           '"to_sdk", "other_to_sdks", "count", and "cursor", '
                           'have invalid values. Values of "from_sdk", '
                           '"other_from_sdks", "to_sdk", "other_to_sdks", and '
                           '"count" must be integers. The correct format for '
                           'the value of "cursor" is '
                           '"<app name>;<app seller name>".',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdk',
                    'other_from_sdks',
                    'to_sdk',
                    'other_to_sdks',
                    'count',
                    'cursor'
                ]
            },
            {
                'message': 'Parameters, "other_from_sdks" and '
                           '"other_to_sdks", must only be specified if the '
                           '"from_sdk" and "to_sdk" parameters are '
                           'unspecified, respectively.',
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
