"""
Tests the /api/v1/sdk-compmatrix/numbers endpoint.
"""
from http import HTTPStatus

from compmatrix.api.views.codes import AnomalyCode
from compmatrix.tests.api.views.test_sdk_compmatrix import (
    BASE_SDK_COMPMATRIX_ENDPOINT
)
from compmatrix.tests.api.views.test_sdk_compmatrix.constants import (
    UNKNOWN_SDK_IDS
)

SDK_COMPMATRIX_NUMBERS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/numbers'


def test_all_row_cols(client, test_db_data, sdk_ids):
    #      Expected Competitive Matrix Values
    #
    #            | PayPal | card.io | Chartboost | (none) |
    # -----------+--------+---------+------------+--------|
    # PayPal     |      4 |       3 |          3 |      0 |
    # card.io    |      2 |       5 |          3 |      2 |
    # Chartboost |      3 |       3 |          4 |      0 |
    # (none)     |      0 |       0 |          0 |      3 |
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
                [3, 3, 4, 0],
                [0, 0, 0, 3]
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
    # (none)     |      0 |      3 |
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
                [3, 7],
                [0, 3]
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
    # (none)     |      4 |     11 |
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
                [4, 10]
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
    # (none)    |      3 |     14 |
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
                [3, 13]
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
    # (none)  |      4 |       4 |          4 |      3 |
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
                [4, 4, 4, 3]
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
    # (none)     |          0 |       0 |      0 |      3 |
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
                [3, 3, 4, 0],
                [0, 0, 0, 3]
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
    # (none)     |      0 |      3 |
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
                [4, 6],
                [0, 3]
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
    # (none)  |       4 |          4 |      4 |      3 |
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
                [4, 4, 4, 3]
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
    # (none)     |      3 |       3 |          4 |      3 |
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
                [3, 3, 4, 3]
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
    # (none)     |      3 |     10 |
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
                [3, 10]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_two_rows_none_col(client, sdk_ids):
    #  Expected Competitive
    #     Matrix Values
    #
    #            | (none) |
    # -----------+--------|
    # PayPal     |     10 |
    # card.io    |     12 |
    # (none)     |     12 |
    query_string = {
        'from_sdks': [sdk_ids[0], sdk_ids[1]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [10],
                [12],
                [12]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_one_row_three_cols(client, sdk_ids):
    #        Expected Competitive Matrix Values
    #
    #        | PayPal | card.io | Chartboost | (none) |
    # -------+--------+---------+------------+--------|
    # (none) |      4 |       5 |          4 |      5 |
    query_string = {
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 5, 4, 5]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_no_row_no_col(client, sdk_ids):
    #    Expected
    #   Competitive
    #  Matrix Values
    #
    #        | (none) |
    # -------+--------|
    # (none) |     17 |
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT)

    expected_resp = {
        'data': {
            'numbers': [
                [16]
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
                'parameters': [
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
                'parameters': ['title', 'artist']
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
                'message': 'Unrecognized parameter, "frm".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': ['frm']
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
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': [
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
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': [
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
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': [
                    'to'
                ]
            },
            {
                'message': 'Parameter, "from_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': ['from_sdks'],
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
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': ['to_sdks'],
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
                'message': 'Unrecognized parameters, "from" and "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': [
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
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': ['to']
            },
            {
                'message': 'Parameter, "from_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': ['from_sdks'],
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
                'message': 'Unrecognized parameter, "from".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': ['from']
            },
            {
                'message': 'Parameter, "to_sdks", has IDs that do not refer '
                           'to an SDK.',
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': ['to_sdks'],
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
                'message': 'Unrecognized parameters, "from" and "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': [
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
                'message': 'Unrecognized parameter, "to".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': ['to']
            },
            {
                'message': 'Parameter, "from_sdks", has an ID that does not '
                           'refer to an SDK.',
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': ['from_sdks'],
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
                'message': 'Unrecognized parameter, "from".',
                'code': AnomalyCode.UNRECOGNIZED_FIELD,
                'parameters': ['from']
            },
            {
                'message': 'Parameter, "to_sdks", has an ID that does not '
                           'refer to an SDK.',
                'code': AnomalyCode.UNKNOWN_ID,
                'parameters': ['to_sdks'],
                'diagnostics': {
                    'to_sdks': unknown_sdks
                }
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_one_invalid_value_from_sdk_param_str_only(client, sdk_ids):
    invalid_values = ['Harder']
    query_string = {
        'from_sdks': invalid_values[0],
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_one_invalid_value_from_sdk_param_num_only(client, sdk_ids):
    invalid_values = ['2.0']
    query_string = {
        'from_sdks': invalid_values[0],
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_from_sdk_words_only(client, sdk_ids):
    invalid_values = ['Harder', 'Better', 'Faster', 'Strong']
    query_string = {
        'from_sdks': invalid_values,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_from_sdk_param_num_only(client, sdk_ids):
    invalid_values = ['1.2', '3.4', '5.61', '6.45']
    query_string = {
        'from_sdks': invalid_values,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_lone_from_sdk_param_words_only(client, sdk_ids):
    invalid_values = ['Harder', 'Better', 'Faster', 'Strong']
    query_string = {
        'from_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_lone_from_sdk_param_num_only(client, sdk_ids):
    invalid_values = ['1.23', '4.56', '7.89', '10.11']
    query_string = {
        'from_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_from_sdk_param_mixed_types(client, sdk_ids):
    invalid_values = ['Harder', '3.5', 'Faster', '4.0']
    query_string = {
        'from_sdks': invalid_values,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_lone_from_sdk_param_mixed_types(client, sdk_ids):
    invalid_values = ['Harder', '3.5', 'Faster', '4.0']
    query_string = {
        'from_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_one_invalid_value_to_sdk_param_words_only(client, sdk_ids):
    invalid_values = ['Harder']
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': invalid_values[0]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_one_invalid_value_to_sdk_param_num_only(client, sdk_ids):
    invalid_values = ['2.0']
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': invalid_values[0]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_to_sdk_words_only(client, sdk_ids):
    invalid_values = ['Harder', 'Better', 'Faster', 'Strong']
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_to_sdk_param_num_only(client, sdk_ids):
    invalid_values = ['1.2', '3.4', '5.61', '6.45']
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_lone_to_sdk_param_words_only(client, sdk_ids):
    invalid_values = ['Harder', 'Better', 'Faster', 'Strong']
    query_string = {
        'to_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_lone_to_sdk_param_num_only(client, sdk_ids):
    invalid_values = ['1.23', '4.56', '7.89', '10.11']
    query_string = {
        'to_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_to_sdk_param_mixed_types(client, sdk_ids):
    invalid_values = ['Harder', '3.5', 'Faster', '4.0']
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_lone_to_sdk_param_mixed_types(client, sdk_ids):
    invalid_values = ['Harder', '3.5', 'Faster', '4.0']
    query_string = {
        'to_sdks': invalid_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_one_invalid_value_sdk_params_words_only(client, sdk_ids):
    invalid_from_sdk_values = ['Bling']
    invalid_to_sdk_values = ['Harder']
    query_string = {
        'from_sdks': invalid_from_sdk_values,
        'to_sdks': invalid_to_sdk_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have '
                           'invalid values. Values of "from_sdks", and '
                           '"to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                    'to_sdks'
                ],
                'diagnostics': {
                    'from_sdks': invalid_from_sdk_values,
                    'to_sdks': invalid_to_sdk_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_one_invalid_value_sdk_params_num_only(client, sdk_ids):
    invalid_from_sdk_values = ['1.65']
    invalid_to_sdk_values = ['3.4']
    query_string = {
        'from_sdks': invalid_from_sdk_values,
        'to_sdks': invalid_to_sdk_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have '
                           'invalid values. Values of "from_sdks", and '
                           '"to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                    'to_sdks'
                ],
                'diagnostics': {
                    'from_sdks': invalid_from_sdk_values,
                    'to_sdks': invalid_to_sdk_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_sdk_params_words_only(client, sdk_ids):
    invalid_from_sdk_values = ['Bling', 'Bang', 'Bang', 'Born']
    invalid_to_sdk_values = ['Harder', 'Better', 'Faster', 'Strong']
    query_string = {
        'from_sdks': invalid_from_sdk_values,
        'to_sdks': invalid_to_sdk_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have '
                           'invalid values. Values of "from_sdks", and '
                           '"to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                    'to_sdks'
                ],
                'diagnostics': {
                    'from_sdks': invalid_from_sdk_values,
                    'to_sdks': invalid_to_sdk_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_invalid_values_sdk_params_num_only(client, sdk_ids):
    invalid_from_sdk_values = ['1.2', '3.4', '5.6', '7.8']
    invalid_to_sdk_values = ['9.1', '23.5', '32.1', '90.4']
    query_string = {
        'from_sdks': invalid_from_sdk_values,
        'to_sdks': invalid_to_sdk_values
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have '
                           'invalid values. Values of "from_sdks", and '
                           '"to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                    'to_sdks'
                ],
                'diagnostics': {
                    'from_sdks': invalid_from_sdk_values,
                    'to_sdks': invalid_to_sdk_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_valid_invalid_values_from_sdk_param(client, sdk_ids):
    invalid_values = ['Bling', '2.34', 'Bang']
    query_string = {
        'from_sdks': [
            sdk_ids[0], invalid_values[0], invalid_values[1],
            sdk_ids[1], invalid_values[2]
        ],
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_lone_mixed_valid_invalid_values_from_sdk(client, sdk_ids):
    invalid_values = ['Bling', '2.45', 'Bang']
    query_string = {
        'from_sdks': [
            sdk_ids[0], invalid_values[0], invalid_values[1],
            sdk_ids[1], invalid_values[2]
        ]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "from_sdks", has invalid values. '
                           'Values of "from_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_valid_invalid_values_to_sdk_param(client, sdk_ids):
    invalid_values = ['Bling', '1.23', 'Bang']
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': [
            sdk_ids[0], invalid_values[0], invalid_values[1],
            sdk_ids[1], invalid_values[2]
        ]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_lone_mixed_valid_invalid_values_to_sdk_param(client, sdk_ids):
    invalid_values = ['Bling', 'Bang', '154.2']
    query_string = {
        'to_sdks': [
            sdk_ids[0], invalid_values[0], invalid_values[1],
            sdk_ids[1], invalid_values[2]
        ]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "to_sdks", has invalid values. '
                           'Values of "to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'to_sdks',
                ],
                'diagnostics': {
                    'to_sdks': invalid_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_valid_invalid_values_sdk_params(client, sdk_ids):
    invalid_from_values = ['Bling', '1.2', 'Bang']
    invalid_to_values = ['3.43', 'to believe in', 'Kung Fury']
    query_string = {
        'from_sdks': [
            sdk_ids[0], invalid_from_values[0], invalid_from_values[1],
            sdk_ids[1], invalid_from_values[2]
        ],
        'to_sdks': [
            sdk_ids[0], invalid_to_values[0], invalid_to_values[1],
            sdk_ids[1], invalid_to_values[2]
        ]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have '
                           'invalid values. Values of "from_sdks", and '
                           '"to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                    'to_sdks',
                ],
                'diagnostics': {
                    'from_sdks': invalid_from_values,
                    'to_sdks': invalid_to_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_mixed_valid_invalid_values_sdk_params1(client, sdk_ids):
    invalid_from_values = ['Bling', '9478.3', 'Bang']
    invalid_to_values = ['123.45', 'to believe in', '678.9']
    query_string = {
        'from_sdks': [
            sdk_ids[0], invalid_from_values[0], invalid_from_values[1],
            sdk_ids[1], invalid_from_values[2]
        ],
        'to_sdks': [
            sdk_ids[0], invalid_to_values[0], invalid_to_values[1],
            sdk_ids[1], invalid_to_values[2]
        ]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameters, "from_sdks" and "to_sdks", have '
                           'invalid values. Values of "from_sdks", and '
                           '"to_sdks" must be integers.',
                'code': AnomalyCode.INVALID_PARAMETER_VALUE,
                'parameters': [
                    'from_sdks',
                    'to_sdks'
                ],
                'diagnostics': {
                    'from_sdks': invalid_from_values,
                    'to_sdks': invalid_to_values
                }
            },
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
