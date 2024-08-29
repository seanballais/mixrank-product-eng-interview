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


# Tests where other_to_sdks is specified.
@pytest.fixture(scope='module')
def paypal_to_none_apps_sans_paypal(apps):
    app_ids = [1, 2, 4, 5, 6, 7]
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


def test_no_cursor(client, paypal_to_none_apps_sans_paypal, sdk_ids):
    apps = paypal_to_none_apps_sans_paypal
    count = 4
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [sdk_ids[0]],
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[:count],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[count - 1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_dir(client, paypal_to_none_apps_sans_paypal, sdk_ids):
    apps = paypal_to_none_apps_sans_paypal
    count = 4
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': '',
        'other_to_sdks': [sdk_ids[0]],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[3:6],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[3]),
            'end_cursor': query_utils.create_app_cursor(apps[5])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_dir2(client, paypal_to_none_apps_sans_paypal,
                              sdk_ids):
    apps = paypal_to_none_apps_sans_paypal
    count = 6
    cursor = query_utils.create_app_cursor(apps[4])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [sdk_ids[0]],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[5:6],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[5]),
            'end_cursor': query_utils.create_app_cursor(apps[5])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_dir(client, paypal_to_none_apps_sans_paypal,
                             sdk_ids):
    apps = paypal_to_none_apps_sans_paypal
    count = 4
    cursor = query_utils.create_app_cursor(apps[3])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [sdk_ids[0]],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[:3],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[2])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_dir2(client, paypal_to_none_apps_sans_paypal,
                              sdk_ids):
    apps = paypal_to_none_apps_sans_paypal
    count = 5
    cursor = query_utils.create_app_cursor(apps[1])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [sdk_ids[0]],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[0:1],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[0])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_no_dir(client, paypal_to_none_apps_sans_paypal, sdk_ids):
    apps = paypal_to_none_apps_sans_paypal
    count = 2
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': [sdk_ids[0]],
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


# Tests where other_to_sdks is not specified.
@pytest.fixture(scope='module')
def paypal_to_only_none_apps(apps):
    app_ids = [0, 1, 2, 3, 4, 5, 6, 7, 9, 12]
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


def test_no_cursor_no_other_to_sdks(client, paypal_to_only_none_apps, sdk_ids):
    apps = paypal_to_only_none_apps
    count = 4
    query_string = {
        'from_sdk': sdk_ids[0],
        'other_to_sdks': '',
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[:count],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[count - 1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_dir_no_other_to_sdks(client, paypal_to_only_none_apps,
                                              sdk_ids):
    apps = paypal_to_only_none_apps
    count = 4
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[3:3 + count],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[3]),
            'end_cursor': query_utils.create_app_cursor(apps[(3 + count) - 1])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_next_dir2_no_other_to_sdks(client,
                                               paypal_to_only_none_apps,
                                               sdk_ids):
    apps = paypal_to_only_none_apps
    count = 7
    cursor = query_utils.create_app_cursor(apps[4])
    query_string = {
        'from_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'next'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[5:10],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[5]),
            'end_cursor': query_utils.create_app_cursor(apps[9])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_dir_no_other_to_sdks(client, paypal_to_only_none_apps,
                                              sdk_ids):
    apps = paypal_to_only_none_apps
    count = 2
    cursor = query_utils.create_app_cursor(apps[3])
    query_string = {
        'from_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[1:3],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[1]),
            'end_cursor': query_utils.create_app_cursor(apps[2])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_prev_dir2_no_other_to_sdks(client,
                                               paypal_to_only_none_apps,
                                               sdk_ids):
    apps = paypal_to_only_none_apps
    count = 5
    cursor = query_utils.create_app_cursor(apps[1])
    query_string = {
        'from_sdk': sdk_ids[0],
        'count': count,
        'cursor': cursor,
        'direction': 'previous'
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'data': {
            'apps': apps[0:1],
            'total_count': len(apps),
            'start_cursor': query_utils.create_app_cursor(apps[0]),
            'end_cursor': query_utils.create_app_cursor(apps[0])
        }
    }

    assert resp.json == expected_resp


def test_has_cursor_no_dir_no_other_to_sdks(client, paypal_to_only_none_apps,
                                            sdk_ids):
    apps = paypal_to_only_none_apps
    count = 2
    cursor = query_utils.create_app_cursor(apps[2])
    query_string = {
        'from_sdk': sdk_ids[0],
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


# Tests to ensure that the `other_to_sdks` parameter is only specified when
# the `to_sdk` parameter is not specified or is an empty string.
def test_has_other_to_sdks_and_to_sdk(client, sdk_ids):
    count = 2
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': [sdk_ids[0]],
        'other_to_sdks': [sdk_ids[1]],
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    expected_resp = {
        'errors': [
            {
                'message': 'Parameter, "other_to_sdks", must only be '
                           'specified if the "to_sdk" parameter is '
                           'unspecified.',
                'code': AnomalyCode.MISUSED_PARAMETER,
                'parameters': [
                    'other_to_sdks'
                ]
            }
        ]
    }

    assert resp.json == expected_resp
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
