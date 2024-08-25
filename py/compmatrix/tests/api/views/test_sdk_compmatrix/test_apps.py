from compmatrix.tests.api.views.test_sdk_compmatrix import (
    BASE_SDK_COMPMATRIX_ENDPOINT
)
from compmatrix.utils import dt

SDK_COMPMATRIX_APPS_ENDPOINT = f'{BASE_SDK_COMPMATRIX_ENDPOINT}/apps'


def test_from_to_sdk_same_ids_no_cursor(client, apps, sdk_ids):
    count = 2
    query_string = {
        'from_sdk': sdk_ids[0],
        'to_sdk': sdk_ids[0],
        'count': count
    }

    resp = client.get(SDK_COMPMATRIX_APPS_ENDPOINT, query_string=query_string)

    app_ids = [0, 3, 9, 12]
    expected_apps = []
    for app_id in app_ids:
        expected_apps.append({
            'id': apps[app_id].id,
            'name': apps[app_id].name,
            'company_url': apps[app_id].company_url,
            'release_date': dt.dt_to_rfc2822_str(apps[app_id].release_date),
            'genre_id': apps[app_id].genre_id,
            'artwork_large_url': apps[app_id].artwork_large_url,
            'seller_name': apps[app_id].seller_name,
            'five_star_ratings': apps[app_id].five_star_ratings,
            'four_star_ratings': apps[app_id].four_star_ratings,
            'three_star_ratings': apps[app_id].three_star_ratings,
            'two_star_ratings': apps[app_id].two_star_ratings,
            'one_star_ratings': apps[app_id].one_star_ratings
        })
    expected_apps.sort(key=lambda a: (a['name'], a['seller_name'],))

    expected_resp = {
        'data': {
            'apps': expected_apps[:count],
            'total_count': len(app_ids),
            'start_cursor': _create_app_cursor(expected_apps[0]),
            'end_cursor': _create_app_cursor(expected_apps[count - 1])
        }
    }

    assert resp.json == expected_resp


def _create_app_cursor(app_obj):
    return f'{app_obj["name"]};{app_obj["seller_name"]}'
