from compmatrix.tests.api.fixtures import test_sdks

from compmatrix.tests.fixtures import app, client

BASE_SDK_COMPMATRIX_ENDPOINT = '/api/v1/sdk-compmatrix'
SDK_COMPMATRIX_NUMBERS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/numbers'


def test_sdks_compmatrix_numbers_endpoint_all_row_cols(client, test_sdks):
    sdk_ids = [sdk.id for sdk in test_sdks]
    query_string = {
        'from_sdks': sdk_ids,
        'to_sdks': sdk_ids
    }
    resp = client.get(SDK_COMPMATRIX_NUMBERS_ENDPOINT,
                      query_string=query_string)

    expected_resp = {
        'numbers': [
            [4, 3, 3],
            [2, 5, 3],
            [3, 3, 4]
        ]
    }

    assert resp.json == expected_resp
