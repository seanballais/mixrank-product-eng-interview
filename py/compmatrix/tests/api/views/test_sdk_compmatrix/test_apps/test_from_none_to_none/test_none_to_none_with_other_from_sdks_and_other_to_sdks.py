"""
Tests where other_from_sdks and other_to_sdks are specified. The expected apps
are the apps that used to use all SDKs except card.io and migrated to other
SDKs except PayPal.
"""
from http import HTTPStatus

import pytest

from compmatrix import model_encoders
from compmatrix.api.views import view_encoders
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.tests.api.views.test_sdk_compmatrix.test_apps import \
    query_utils
from compmatrix.utils import dt

from .constants import SDK_COMPMATRIX_APPS_ENDPOINT


@pytest.fixture(scope='module')
def expected_apps(apps):
    app_ids = [1, 2, 4, 5, 6, 7, 8, 12]
    expected_apps = []
    for app_id in app_ids:
        encoded_obj = view_encoders.encode_app_model_object(apps[app_id])
        expected_apps.append(encoded_obj)
    expected_apps.sort(key=lambda a: (a['name'], a['seller_name'],))

    yield expected_apps


def test_no_cursor(client, expected_apps, sdk_ids):
    apps = expected_apps
    count = 4
    query_string = {
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': sdk_ids[0],
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[:count],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[3])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_dir(client, expected_apps, sdk_ids):
    apps = expected_apps
    count = 2
    cursor = query_utils.create_app_cursor(apps[1])
    query_string = {
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[2:4],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[2]),
            'end_cursor': query_utils.create_app_cursor(apps[3])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_dir2(client, expected_apps, sdk_ids):
    apps = expected_apps
    count = 15
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[3:8],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[3]),
            'end_cursor': query_utils.create_app_cursor(apps[7])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_dir(client, expected_apps, sdk_ids):
    apps = expected_apps
    count = 2
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[:2],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_dir2(client, expected_apps, sdk_ids):
    apps = expected_apps
    count = 5
    cursor = query_utils.create_app_cursor(apps[3])
    query_string = {
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[0:3],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[2])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_no_dir(client, expected_apps, sdk_ids):
    apps = expected_apps
    count = 2
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'other_from_sdks': [sdk_ids[1]],
        'other_to_sdks': sdk_ids[0],
        'count': count,
        'cursor': cursor
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Required parameter, "direction", is missing. '
                           'It is required when the "cursor" parameter '
                           'has a value.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'direction'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
