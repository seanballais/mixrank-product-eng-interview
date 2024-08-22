"""
Tests the /api/v1/sdk-compmatrix/numbers endpoint.
"""
from http import HTTPStatus

import pytest

from compmatrix.api.views.codes import AnomalyCode

from compmatrix.tests.conftest import app, client
from compmatrix.tests.api.views.test_sdk_compmatrix import (
    BASE_SDK_COMPMATRIX_ENDPOINT
)

SDK_COMPMATRIX_NUMBERS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/numbers'

# Try converting the integers immediately below to hex. ;-)
UNKNOWN_SDK_IDS = [3737844653, 3405697037, 3669732608]


@pytest.fixture(scope='session')
def sdk_ids(test_db_data):
    yield [sdk.id for sdk in test_db_data['sdks']]


def test_all_row_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive Matrix Values
    #
    #            | PayPal | card.io | Chartboost | (none) |
    # -----------+--------+---------+------------+--------|
    # PayPal     |      4 |       3 |          3 |      0 |
    # card.io    |      2 |       5 |          3 |      2 |
    # Chartboost |      3 |       3 |          4 |      0 |
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 3, 3, 0],
                [2, 5, 3, 2],
                [3, 3, 4, 0]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_all_row_one_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # PayPal     |      4 |      6 |
    # card.io    |      2 |     10 |
    # Chartboost |      3 |      7 |
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': [sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 6],
                [2, 10],
                [3, 7]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_one_row_one_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # card.io    |      2 |     10 |
    # (none)     |      4 |      8 |
    query_string = {
        'from_sdks': [sdk_ids[1]],
        'to_sdks': [sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [2, 10],
                [4, 8]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_one_row_one_cols2(client, test_db_data, sdk_ids):
    #      Expected Competitive
    #         Matrix Values
    #
    #           | PayPal | (none) |
    # ----------+--------+--------|
    # Paypal    |      4 |      6 |
    # (none)    |      3 |     11 |
    query_string = {
        'from_sdks': [sdk_ids[0]],
        'to_sdks': [sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 6],
                [3, 11]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_one_row_all_cols(client, test_db_data, sdk_ids):
    #    Expected Competitive Matrix Values
    #
    #         | PayPal | card.io | Chartboost | (none) |
    # --------+--------+---------+------------+--------|
    # card.io |      2 |       5 |          3 |      2 |
    # (none)  |      4 |       4 |          4 |      0 |
    query_string = {
        'from_sdks': [sdk_ids[1]],
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [2, 5, 3, 2],
                [4, 4, 4, 0]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_all_row_cols_shuffled1(client, test_db_data, sdk_ids):
    #      Expected Competitive Matrix Values
    #
    #            | Chartboost | card.io | PayPal | (none) |
    # -----------+------------|---------+--------+--------|
    # Chartboost |          4 |       3 |      3 |      0 |
    # card.io    |          3 |       5 |      2 |      2 |
    # PayPal     |          3 |       3 |      4 |      0 |
    shuffled_sdk_ids: list[int] = [sdk_ids[2], sdk_ids[1], sdk_ids[0]]
    query_string = {
        'from_sdks': shuffled_sdk_ids,
        'to_sdks': shuffled_sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 3, 3, 0],
                [3, 5, 2, 2],
                [3, 3, 4, 0]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_all_row_shuffled1_one_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # card.io    |      2 |     10 |
    # Chartboost |      3 |      7 |
    # PayPal     |      4 |      6 |
    query_string = {
        'from_sdks': [sdk_ids[1], sdk_ids[2], sdk_ids[0]],
        'to_sdks': [sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [2, 10],
                [3, 7],
                [4, 6]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_one_row_all_cols_shuffled1(client, test_db_data, sdk_ids):
    #    Expected Competitive Matrix Values
    #
    #         | card.io | Chartboost | PayPal | (none) |
    # --------+---------+------------|--------+--------|
    # card.io |       5 |          3 |      2 |      2 |
    # (none)  |       4 |          4 |      4 |      0 |
    query_string = {
        'from_sdks': [sdk_ids[1]],
        'to_sdks': [sdk_ids[1], sdk_ids[2], sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [5, 3, 2, 2],
                [4, 4, 4, 0]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_two_rows_all_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive Matrix Values
    #
    #            | PayPal | card.io | Chartboost | (none) |
    # -----------+--------+---------+------------+--------|
    # PayPal     |      4 |       3 |          3 |      0 |
    # card.io    |      2 |       5 |          3 |      2 |
    # (none)     |      3 |       3 |          4 |      0 |
    query_string = {
        'from_sdks': [sdk_ids[0], sdk_ids[1]],
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 3, 3, 0],
                [2, 5, 3, 2],
                [3, 3, 4, 0]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_two_rows_one_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # PayPal     |      4 |      6 |
    # card.io    |      2 |     10 |
    # (none)     |      3 |      7 |
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': [sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 6],
                [2, 10],
                [3, 7]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_error_unknown_params(client, test_db_data, sdk_ids):
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': sdk_ids,
        'title': 'Shalala Lala',
        'artist': 'Vengaboys',
        'chorus1': 'My heart goes shalalalala',
        'music1': '(clap clap clap)',
        'chorus2': 'Shalala in the mooooorniiiiiinggg',
        'chorus3': 'Shalalalala',
        'chorus4': 'Shalala in the suuuuunnnshiiiinnneeee',
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Unrecognized parameters, "title", "artist", '
                           '"chorus1", "music1", "chorus2", "chorus3", '
                           'and "chorus4".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': [
                    'title',
                    'artist',
                    'chorus1',
                    'music1',
                    'chorus2',
                    'chorus3',
                    'chorus4'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_error_two_unknown_params(client, test_db_data, sdk_ids):
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': sdk_ids,
        'title': 'Shalala Lala',
        'artist': 'Vengaboys'
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Unrecognized parameters, "title" and "artist".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': ['title', 'artist']
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_no_params(client, test_db_data):
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameters, "from_sdks" and "to_sdks", '
                           'are missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'from_sdks',
                    'to_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_no_from_sdks(client, test_db_data, sdk_ids):
    query_string = {
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "from_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['from_sdks']
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_no_to_sdks(client, test_db_data, sdk_ids):
    query_string = {
        'from_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "to_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_typo_from_sdks(client, test_db_data, sdk_ids):
    query_string = {
        'frm': sdk_ids,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "from_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'from_sdks',
                ]
            },
            {
                'message': 'Unrecognized parameter, "frm".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': ['frm']
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_typo_to_sdks(client, test_db_data, sdk_ids):
    query_string = {
        'from_sdks': sdk_ids,
        'to': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "to_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            },
            {
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': [
                    'to'
                ]
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_unknown_sdks_in_from_to_param(client, test_db_data):
    query_string = {
        'from_sdks': UNKNOWN_SDK_IDS,
        'to_sdks': UNKNOWN_SDK_IDS
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have IDs '
                           'that do not refer to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': [
                    'from_sdks',
                    'to_sdks'
                ],
                'diagnostics': {
                    'from_sdks': UNKNOWN_SDK_IDS,
                    'to_sdks': UNKNOWN_SDK_IDS
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_unknown_sdks_in_from_param(client, test_db_data, sdk_ids):
    query_string = {
        'from_sdks': UNKNOWN_SDK_IDS,
        'to': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "to_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            },
            {
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': [
                    'to'
                ]
            },
            {
                'message': 'Parameter, "from_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': ['from_sdks'],
                'diagnostics': {
                    'from_sdks': UNKNOWN_SDK_IDS
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_unknown_sdks_in_to_param(client, test_db_data, sdk_ids):
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': UNKNOWN_SDK_IDS
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': ['to_sdks'],
                'diagnostics': {
                    'to_sdks': UNKNOWN_SDK_IDS
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_unknown_sdks_in_from_to_param(client, test_db_data, sdk_ids):
    mixed_ids = [
        UNKNOWN_SDK_IDS[0], sdk_ids[0], sdk_ids[1],
        UNKNOWN_SDK_IDS[1], sdk_ids[2]
    ]
    unknown_sdks = [mixed_ids[0], mixed_ids[3]]
    query_string = {
        'from': unknown_sdks,
        'to': unknown_sdks
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameters, "from_sdks" and "to_sdks", '
                           'are missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'from_sdks',
                    'to_sdks'
                ]
            },
            {
                'message': 'Unrecognized parameters, "from" and "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': [
                    'from',
                    'to'
                ]
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_unknown_sdks_in_from_param(client, test_db_data, sdk_ids):
    mixed_ids = [
        UNKNOWN_SDK_IDS[0], sdk_ids[0], sdk_ids[1],
        UNKNOWN_SDK_IDS[1], sdk_ids[2]
    ]
    unknown_sdks = [mixed_ids[0], mixed_ids[3]]
    query_string = {
        'from_sdks': mixed_ids,
        'to': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "to_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            },
            {
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': ['to']
            },
            {
                'message': 'Parameter, "from_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': ['from_sdks'],
                'diagnostics': {
                    'from_sdks': unknown_sdks
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_unknown_sdks_in_to_param(client, test_db_data, sdk_ids):
    mixed_ids = [UNKNOWN_SDK_IDS[0], sdk_ids[0], sdk_ids[1],
                 UNKNOWN_SDK_IDS[1],
                 sdk_ids[2]]
    unknown_sdks = [mixed_ids[0], mixed_ids[3]]
    query_string = {
        'from': sdk_ids,
        'to_sdks': unknown_sdks
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "from_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['from_sdks']
            },
            {
                'message': 'Unrecognized parameter, "from".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': ['from']
            },
            {
                'message': 'Parameter, "to_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': ['to_sdks'],
                'diagnostics': {
                    'to_sdks': unknown_sdks
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_unknown_sdks_in_from_to_param_one_unknown(client, test_db_data,
                                                         sdk_ids):
    mixed_ids = [UNKNOWN_SDK_IDS[0], sdk_ids[0], sdk_ids[1], sdk_ids[2]]
    unknown_sdks = [mixed_ids[0]]
    query_string = {
        'from': unknown_sdks,
        'to': unknown_sdks
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameters, "from_sdks" and "to_sdks", '
                           'are missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'from_sdks',
                    'to_sdks'
                ]
            },
            {
                'message': 'Unrecognized parameters, "from" and "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': [
                    'from',
                    'to'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_unknown_sdks_in_from_param_one_unknown(client, test_db_data,
                                                      sdk_ids):
    from_ids = [UNKNOWN_SDK_IDS[0], sdk_ids[0], sdk_ids[1], sdk_ids[2]]
    unknown_sdks = [from_ids[0]]
    query_string = {
        'from_sdks': from_ids,
        'to': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "to_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            },
            {
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': ['to']
            },
            {
                'message': 'Parameter, "from_sdks", has an ID that does not '
                           'refer to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': ['from_sdks'],
                'diagnostics': {
                    'from_sdks': unknown_sdks
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_unknown_sdks_in_to_param_one_unknown(client, test_db_data,
                                                    sdk_ids):
    to_ids = [UNKNOWN_SDK_IDS[0], sdk_ids[0], sdk_ids[1], sdk_ids[2]]
    unknown_sdks = [to_ids[0]]
    query_string = {
        'from': sdk_ids,
        'to_sdks': unknown_sdks
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "from_sdks", is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['from_sdks']
            },
            {
                'message': 'Unrecognized parameter, "from".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'fields': ['from']
            },
            {
                'message': 'Parameter, "to_sdks", has an ID that does not '
                           'refer to an SDK.',
                'code': AnomalyCode.UNKNOWN_IDS,
                'fields': ['to_sdks'],
                'diagnostics': {
                    'to_sdks': unknown_sdks
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
