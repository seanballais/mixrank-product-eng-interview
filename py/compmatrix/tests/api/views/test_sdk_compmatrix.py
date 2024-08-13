from http import HTTPStatus

from compmatrix.api.views.codes import AnomalyCode
from compmatrix.tests.api.fixtures import test_sdks

from compmatrix.tests.fixtures import app, client

BASE_SDK_COMPMATRIX_ENDPOINT = '/api/v1/sdk-compmatrix'
SDK_COMPMATRIX_NUMBERS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/numbers'


def test_numbers_endpoint_all_row_cols(client, test_sdks):
    sdk_ids = [sdk.id for sdk in test_sdks]
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


def test_numbers_endpoint_warn_unknown_params(client, test_sdks):
    print('1')
    sdk_ids = [sdk.id for sdk in test_sdks]
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


def test_numbers_endpoint_no_params(client, test_sdks):
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


def test_numbers_endpoint_no_from_sdks(client, test_sdks):
    sdk_ids = [sdk.id for sdk in test_sdks]
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


def test_numbers_endpoint_typo_from_sdks(client, test_sdks):
    sdk_ids = [sdk.id for sdk in test_sdks]
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


def test_numbers_endpoint_no_to_sdks(client, test_sdks):
    sdk_ids = [sdk.id for sdk in test_sdks]
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


def test_numbers_endpoint_typo_to_sdks(client, test_sdks):
    sdk_ids = [sdk.id for sdk in test_sdks]
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
