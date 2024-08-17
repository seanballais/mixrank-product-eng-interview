from http import HTTPStatus

from compmatrix.api.views.codes import AnomalyCode

from compmatrix.tests.conftest import app, client

BASE_SDK_COMPMATRIX_ENDPOINT = '/api/v1/sdk-compmatrix'
SDK_COMPMATRIX_NUMBERS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/numbers'


def test_numbers_endpoint_all_row_cols(client, test_db_data):
    #      Expected Competitive Matrix Values
    #
    #            | PayPal | card.io | Chartboost |
    # -----------+--------+---------+------------|
    # PayPal     |      4 |       3 |          3 |
    # card.io    |      2 |       5 |          3 |
    # Chartboost |      3 |       3 |          4 |
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 3, 3],
                [2, 5, 3],
                [3, 3, 4]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_numbers_endpoint_all_row_one_cols(client, test_db_data):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # PayPal     |      4 |      6 |
    # card.io    |      2 |      8 |
    # Chartboost |      3 |      7 |
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
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
                [2, 8],
                [3, 7]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_numbers_endpoint_one_row_one_cols(client, test_db_data):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # card.io    |      2 |      8 |
    # (none)     |      4 |      8 |
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': [sdk_ids[1]],
        'to_sdks': [sdk_ids[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [2, 8],
                [4, 8]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_numbers_endpoint_one_row_all_cols(client, test_db_data):
    #    Expected Competitive Matrix Values
    #
    #         | PayPal | card.io | Chartboost |
    # --------+--------+---------+------------|
    # card.io |      2 |       5 |          3 |
    # (none)  |      4 |       4 |          4 |
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': [sdk_ids[1]],
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [2, 5, 3],
                [4, 4, 4]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


# TODO: Add test cases where the order of IDs are different.
def test_numbers_endpoint_all_row_cols_shuffled1(client, test_db_data):
    #      Expected Competitive Matrix Values
    #
    #            | Chartboost | card.io | PayPal |
    # -----------+------------|---------+--------+
    # Chartboost |          4 |       3 |      3 |
    # card.io    |          3 |       5 |      2 |
    # PayPal     |          3 |       3 |      4 |
    sdks = [sdk.id for sdk in test_db_data['sdks']]
    sdk_ids = [sdks[2], sdks[1], sdks[0]]
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [4, 3, 3],
                [3, 5, 2],
                [3, 3, 4]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_numbers_endpoint_all_row_shuffled1_one_cols(client, test_db_data):
    #      Expected Competitive
    #         Matrix Values
    #
    #            | PayPal | (none) |
    # -----------+--------+--------|
    # card.io    |      2 |      8 |
    # Chartboost |      3 |      7 |
    # PayPal     |      4 |      6 |
    sdks = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': [sdks[1], sdks[2], sdks[0]],
        'to_sdks': [sdks[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [2, 8],
                [3, 7],
                [4, 6]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_numbers_endpoint_one_row_all_cols_shuffled1(client, test_db_data):
    #    Expected Competitive Matrix Values
    #
    #         | card.io | Chartboost | PayPal |
    # --------+---------+------------|--------+
    # card.io |       5 |          3 |      2 |
    # (none)  |       4 |          4 |      4 |
    sdks = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': [sdks[1]],
        'to_sdks': [sdks[1], sdks[2], sdks[0]]
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'data': {
            'numbers': [
                [5, 3, 2],
                [4, 4, 4]
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


# TODO: Add test cases where there are two rows with specific SDKs and one row
#       as the "(none)" row.


def test_numbers_endpoint_warn_unknown_params(client, test_db_data):
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
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
        'data': {
            'numbers': [
                [4, 3, 3],
                [2, 5, 3],
                [3, 3, 4]
            ]
        },
        'warning': {
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
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.OK


def test_numbers_endpoint_no_params(client, test_db_data):
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT)

    expected_resp = {
        'error': {
            'message': 'Required parameters, from_sdks and to_sdks, '
                       'are missing.',
            'code': AnomalyCode.MISSING_FIELD,
            'fields': [
                'from_sdks',
                'to_sdks'
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_numbers_endpoint_no_from_sdks(client, test_db_data):
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'error': {
            'message': 'Required parameter, from_sdks, is missing.',
            'code': AnomalyCode.MISSING_FIELD,
            'fields': ['from_sdks']
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_numbers_endpoint_typo_from_sdks(client, test_db_data):
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'frm': sdk_ids,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'error': {
            'message': 'Required parameter, from_sdks, is missing.',
            'code': AnomalyCode.MISSING_FIELD,
            'fields': [
                'from_sdks',
            ]
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_numbers_endpoint_no_to_sdks(client, test_db_data):
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'error': {
            'message': 'Required parameter, to_sdks, is missing.',
            'code': AnomalyCode.MISSING_FIELD,
            'fields': ['to_sdks']
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_numbers_endpoint_typo_to_sdks(client, test_db_data):
    sdk_ids = [sdk.id for sdk in test_db_data['sdks']]
    query_string = {
        'from_sdks': sdk_ids,
        'to': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'error': {
            'message': 'Required parameter, to_sdks, is missing.',
            'code': AnomalyCode.MISSING_FIELD,
            'fields': ['to_sdks']
        }
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

# TODO: Add test cases where unknown IDs were used.
