from datetime import datetime

import pytest

from compmatrix import model_encoders
from compmatrix.tests.api.views.test_sdk_compmatrix import (
    BASE_SDK_COMPMATRIX_ENDPOINT
)
from compmatrix.utils import dt

SDK_COMPMATRIX_APPS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/apps'


@pytest.fixture(scope='module')
def paypal_to_paypal_apps(apps):
    app_ids = [0, 3, 9, 12]
    expected_apps = []
    for app_id in app_ids:
        ignored_fields = ['sdks']
        filters = [
            model_encoders.ModelEncoderFilter(
                'release_date', dt.dt_to_rfc2822_str
            )
        ]
        encoded_model = model_encoders.encode_model_as_dict(apps[app_id],
                                                            ignored_fields,
                                                            filters)

        expected_apps.append(encoded_model)
    expected_apps.sort(key=lambda a: (a['name'], a['seller_name'],))

    yield expected_apps


def test_from_to_sdk_same_ids_no_cursor(client, paypal_to_paypal_apps,
                                        sdk_ids):
    count = 2
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': paypal_to_paypal_apps[:count],
            'total_count': len(paypal_to_paypal_apps),
            'start_cursor': _create_app_cursor(paypal_to_paypal_apps[0]),
            'end_cursor': _create_app_cursor(paypal_to_paypal_apps[count - 1])
        }
    }

    assert resp.json == expected_resp


def _create_app_cursor(app_obj):
    return f'{app_obj["name"]};{app_obj["seller_name"]}'
