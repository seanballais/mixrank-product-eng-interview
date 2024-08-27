from http import HTTPStatus

from flask import request
from flask_sqlalchemy.query import Query
from sqlalchemy import Subquery, Tuple

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views import messages
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.api.views.sdk_compmatrix import queries
from compmatrix.utils import dt


def index():
    """
    Returns the apps that previously and currently have installed the SDKs
    specified in the parameters.
    """
    resp: dict[str, object | list] = {}

    from_sdk_param: int = int(request.args.get('from_sdk'))

    to_sdk_param: int | None = None
    other_to_sdks_param: list[int] = []
    if 'to_sdk' in request.args and request.args.get('to_sdk') != '':
        to_sdk_param = int(request.args.get('to_sdk'))
    else:
        other_to_sdks_param = [
            int(s) for s in request.args.getlist('other_to_sdks')
        ]

    count_param: int = int(request.args.get('count'))

    cursor_param: str | None = request.args.get('cursor')
    direction_param: str | None = None
    if cursor_param:
        cursor_param: str = str(cursor_param)

        if 'direction' in request.args:
            direction_param: str = str(request.args.get('direction'))
        else:
            if 'errors' not in resp:
                resp['errors'] = []

            missing_param: list[str] = ['direction']
            message: str = messages.create_missing_params_message(
                missing_param)
            message = (
                f'{message} It is required when the "cursor" parameter '
                'has a value.'
            )
            resp['errors'].append({
                'message': message,
                'code': AnomalyCode.MISSING_FIELD,
                'fields': list(missing_param)
            })

    if 'errors' in resp:
        return resp, HTTPStatus.UNPROCESSABLE_ENTITY

    if to_sdk_param is None:
        included_apps_query: Subquery = queries.get_query_for_from_sdk_to_none(
            from_sdk_param, other_to_sdks_param
        ).subquery()
    else:
        included_apps_query: Subquery = queries.get_query_for_from_to_sdks(
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
        cursor_vals: Tuple = db.tuple_(*cursor_param.split(';'))
        columns: Tuple = db.tuple_(models.App.name, models.App.seller_name)

        if direction_param == 'previous':
            # We're using less than because the query will have the results
            # ordered descendingly, when the direction is "previous".
            apps_query = apps_query.where(columns < cursor_vals)
        else:
            # direction_param == 'next'. Note that we are expecting that our
            # guard code will check if any of the parameters have invalid
            # values.
            apps_query = apps_query.where(columns > cursor_vals)

    if cursor_param and direction_param == 'previous':
        apps_query = (
            apps_query
            .order_by(
                db.desc(models.App.name),
                db.desc(models.App.seller_name)
            )
        )
    else:
        apps_query = (
            apps_query
            .order_by(
                db.asc(models.App.name),
                db.asc(models.App.seller_name)
            )
        )

    apps_query = apps_query.limit(count_param)
    apps: list[models.App] = apps_query.all()

    if cursor_param and direction_param == 'previous':
        # We need to reverse the order of the results if the direction was
        # set to 'previous', since we're reversing the order earlier to get
        # the correct values. Now, we're reversing the order once again to
        # get the correct ordering. So far, we're just reversing the list
        # to make our code simpler. However, we should implement some
        # benchmarks to see if reversing the list from Python is faster than
        # reversing the list via SQL.
        apps.reverse()

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
