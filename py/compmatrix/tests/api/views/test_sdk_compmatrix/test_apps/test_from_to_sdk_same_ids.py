from http import HTTPStatus

import pytest

from compmatrix import model_encoders
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.tests.api.views.test_sdk_compmatrix import (
    BASE_SDK_COMPMATRIX_ENDPOINT
)
from compmatrix.tests.api.views.test_sdk_compmatrix.test_apps import (
    query_utils
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


def test_no_cursor(client, paypal_to_paypal_apps, sdk_ids):
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
            'start_cursor': query_utils.create_cursor_from_app_dict(
                paypal_to_paypal_apps[0]),
            'end_cursor': query_utils.create_cursor_from_app_dict(
                paypal_to_paypal_apps[count - 1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_direction(client, paypal_to_paypal_apps, sdk_ids):
    apps = paypal_to_paypal_apps
    count = 2
    cursor = query_utils.create_cursor_from_app_dict(apps[1])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[2:2 + count],
            'total_count': len(apps),
            'start_cursor': query_utils.create_cursor_from_app_dict(
                apps[count]),
            'end_cursor': query_utils.create_cursor_from_app_dict(
                apps[(count * 2) - 1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_direction2(client, paypal_to_paypal_apps, sdk_ids):
    apps = paypal_to_paypal_apps
    count = 2
    cursor = query_utils.create_cursor_from_app_dict(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[3:4],
            'total_count': len(apps),
            'start_cursor': query_utils.create_cursor_from_app_dict(apps[3]),
            'end_cursor': query_utils.create_cursor_from_app_dict(apps[3])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_direction(client, paypal_to_paypal_apps, sdk_ids):
    apps = paypal_to_paypal_apps
    count = 2
    cursor = query_utils.create_cursor_from_app_dict(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[:count],
            'total_count': len(apps),
            'start_cursor': query_utils.create_cursor_from_app_dict(apps[0]),
            'end_cursor': query_utils.create_cursor_from_app_dict(
                apps[count - 1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_direction2(client, paypal_to_paypal_apps, sdk_ids):
    apps = paypal_to_paypal_apps
    count = 2
    cursor = query_utils.create_cursor_from_app_dict(apps[1])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[0:1],
            'total_count': len(apps),
            'start_cursor': query_utils.create_cursor_from_app_dict(apps[0]),
            'end_cursor': query_utils.create_cursor_from_app_dict(apps[0])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_no_direction(client, paypal_to_paypal_apps, sdk_ids):
    apps = paypal_to_paypal_apps
    count = 2
    cursor = query_utils.create_cursor_from_app_dict(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "direction", is missing. '
                           'It is required when the "cursor" parameter '
                           'is specified.',
                'code': AnomalyCode.MISSING_FIELD,
                'parameters': [
                    'direction'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
