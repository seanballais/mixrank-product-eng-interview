from flask import request
from flask_sqlalchemy.query import Query
from sqlalchemy import Select

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views.sdk_compmatrix import queries
from compmatrix.utils import dt


def index():
    """
    Returns the apps that previously and currently have installed the SDKs
    specified in the parameters.
    """
    from_sdk_param: int = int(request.args.get('from_sdk'))
    to_sdk_param: int = int(request.args.get('to_sdk'))
    count_param: int = int(request.args.get('count'))

    cursor_param: str | None = request.args.get('cursor')
    direction_param: str | None = None
    if cursor_param:
        cursor_param: str = str(cursor_param)
        direction_param: str = str(request.args.get('direction'))

    included_apps_query = queries.get_query_for_from_to_sdks(
        from_sdk_param, to_sdk_param
    ).subquery()
    num_apps: int = db.session.execute(
        db.select(db.func.count('*')).select_from(included_apps_query)
    ).scalar_one()

    apps_query: Query = (
        models.App.query.join(
            included_apps_query, models.App.id == included_apps_query.c.app_id
        )
    )
    if cursor_param:
        cursor_vals: tuple = db.tuple_(*cursor_param.split(';'))
        apps_query = apps_query.where(
            db.tuple_(models.App.name, models.App.seller_name) > cursor_vals
        )
    apps_query = (
        apps_query
        .order_by(models.App.name, models.App.seller_name)
        .limit(count_param)
    )
    print(apps_query)

    apps: list[models.App] = apps_query.all()

    resp_apps: list[dict] = []
    for app in apps:
        resp_apps.append({
            'id': app.id,
            'name': app.name,
            'company_url': app.company_url,
            'release_date': dt.dt_to_rfc2822_str(app.release_date),
            'genre_id': app.genre_id,
            'artwork_large_url': app.artwork_large_url,
            'seller_name': app.seller_name,
            'five_star_ratings': app.five_star_ratings,
            'four_star_ratings': app.four_star_ratings,
            'three_star_ratings': app.three_star_ratings,
            'two_star_ratings': app.two_star_ratings,
            'one_star_ratings': app.one_star_ratings
        })

    return {
        'data': {
            'apps': resp_apps,
            'total_count': num_apps,
            'start_cursor': _create_cursor_from_app(apps[0]),
            'end_cursor': _create_cursor_from_app(apps[-1])
        }
    }


def _create_cursor_from_app(app: models.App) -> str:
    return f'{app.name};{app.seller_name}'
