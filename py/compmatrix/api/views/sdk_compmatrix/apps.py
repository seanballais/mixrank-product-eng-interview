import dataclasses
from collections import OrderedDict
from http import HTTPStatus

from flask import request
from flask_sqlalchemy.query import Query
from sqlalchemy import Subquery, Tuple, Select, CompoundSelect
from werkzeug.datastructures import MultiDict

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views import messages, queries, checks
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.api.views import view_encoders
from compmatrix.api.views.parameters import ParamPartnership


@dataclasses.dataclass
class MisusedParamGroup:
    parameters: list[str]
    partnership: ParamPartnership


def index():
    """
    Returns the apps that previously and currently have installed the SDKs
    specified in the parameters.
    """
    resp: dict[str, object | list] = {}

    known_params: list[str] = [
        'from_sdk',
        'to_sdk',
        'other_from_sdks',
        'other_to_sdks',
        'count',
        'cursor',
        'direction'
    ]
    partner_params: dict[str, str] = {
        'from_sdk': 'other_from_sdks',
        'to_sdk': 'other_to_sdks',
        'other_from_sdks': 'from_sdk',
        'other_to_sdks': 'to_sdk',
        'cursor': 'direction',
        'direction': 'cursor'
    }

    params_with_sdk_ids_to_check: OrderedDict = OrderedDict()

    client_params: MultiDict[str, str] = request.args

    unknown_params: list[str] = [
        k for k in client_params.keys() if k not in known_params
    ]
    if unknown_params:
        if 'errors' not in resp:
            resp['errors'] = []

        message: str = messages.create_unknown_params_message(unknown_params)
        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.UNRECOGNIZED_FIELD,
            'parameters': unknown_params
        })

    misused_params_groups: list[MisusedParamGroup] = []
    wrong_valued_params: list[str] = []

    misused_sdk_params: list[str] = []

    from_sdk_param: int | None = None
    other_from_sdks_param: list[int] = []
    if 'from_sdk' in client_params and client_params.get('from_sdk') != '':
        try:
            from_sdk_param = int(client_params.get('from_sdk'))
            params_with_sdk_ids_to_check['from_sdk'] = from_sdk_param
        except ValueError:
            wrong_valued_params.append('from_sdk')

        if 'other_from_sdks' in client_params:
            misused_sdk_params.append('other_from_sdks')

    # We need to check the values of other_from_sdks even if they are not
    # supposed to be specified.
    has_bad_val: bool = False
    for s in client_params.getlist('other_from_sdks'):
        if s != '':
            try:
                sdk: int = int(s)
                other_from_sdks_param.append(sdk)
            except ValueError:
                has_bad_val = True

    if has_bad_val:
        wrong_valued_params.append('other_from_sdks')

    params_with_sdk_ids_to_check['other_from_sdks'] = other_from_sdks_param

    to_sdk_param: int | None = None
    other_to_sdks_param: list[int] = []
    if 'to_sdk' in client_params and client_params.get('to_sdk') != '':
        try:
            to_sdk_param = int(client_params.get('to_sdk'))
            params_with_sdk_ids_to_check['to_sdk'] = to_sdk_param
        except ValueError:
            wrong_valued_params.append('to_sdk')

        if 'other_to_sdks' in client_params:
            misused_sdk_params.append('other_to_sdks')

    # We need to check the values of other_from_sdks even if they are not
    # supposed to be specified.
    has_bad_val: bool = False
    for s in client_params.getlist('other_to_sdks'):
        if s != '':
            try:
                sdk: int = int(s)
                other_to_sdks_param.append(sdk)
            except ValueError:
                has_bad_val = True

    if has_bad_val:
        wrong_valued_params.append('other_to_sdks')

    params_with_sdk_ids_to_check['other_to_sdks'] = other_to_sdks_param

    if misused_sdk_params:
        misused_params_groups.append(
            MisusedParamGroup(misused_sdk_params, ParamPartnership.INVERSE))

    count_param: int | None = None
    try:
        count_param = int(client_params.get('count'))
    except ValueError:
        wrong_valued_params.append('count')

    cursor_param: str | None = client_params.get('cursor')
    if cursor_param:
        cursor_parts: list[str] = cursor_param.split(';')
        if len(cursor_parts) != 2:
            wrong_valued_params.append('cursor')
    else:
        cursor_parts: list[str] = []

    # We need to also check the value of the direction parameter, where the
    # cursor parameter exists or not.
    if 'direction' in client_params:
        direction_param: str = client_params.get('direction')
        if direction_param != "previous" and direction_param != "next":
            wrong_valued_params.append('direction')
    else:
        direction_param: None = None

    if cursor_param:
        cursor_param: str = str(cursor_param)

        if 'direction' not in client_params:
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
                'parameters': list(missing_param)
            })
    elif direction_param is not None:
        # direction parameter specified even if cursor was not.
        misused_params_groups.append(
            MisusedParamGroup(['direction'], ParamPartnership.COUPLED))

    if wrong_valued_params:
        if 'errors' not in resp:
            resp['errors'] = []

        message: str = messages.create_wrong_valued_params_message(
            wrong_valued_params)
        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.INVALID_PARAMETER_VALUE,
            'parameters': wrong_valued_params
        })

    if params_with_sdk_ids_to_check:
        checks.check_for_unknown_ids_in_params(resp,
                                               params_with_sdk_ids_to_check)

    if misused_params_groups:
        if 'errors' not in resp:
            resp['errors'] = []

        message_parts: list[str] = []
        for group in misused_params_groups:
            message_parts.append(
                messages.create_misused_params_message(group, partner_params))

        message: str = ' '.join(message_parts)

        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.MISUSED_PARAMETER,
            'parameters': [
                p for g in misused_params_groups for p in g.parameters
            ]
        })

    if 'errors' in resp:
        return resp, HTTPStatus.UNPROCESSABLE_ENTITY

    if from_sdk_param is None and to_sdk_param is None:
        included_apps_query: Select = queries.get_query_for_none_to_none(
            other_from_sdks_param, other_to_sdks_param
        )
    elif from_sdk_param is None and to_sdk_param is not None:
        included_apps_query: Select = queries.get_query_for_none_to_to_sdk(
            to_sdk_param, other_from_sdks_param)
    elif to_sdk_param is None and from_sdk_param is not None:
        included_apps_query: CompoundSelect = (
            queries.get_query_for_from_sdk_to_none(from_sdk_param,
                                                   other_to_sdks_param)
        )
    else:
        included_apps_query: Select = queries.get_query_for_from_to_sdks(
            from_sdk_param, to_sdk_param
        )
    included_apps_query: Subquery = included_apps_query.subquery()
    num_apps: int = db.session.execute(
        db.select(db.func.count('*')).select_from(included_apps_query)
    ).scalar_one()

    apps_query: Query = (
        models.App.query.join(
            included_apps_query, models.App.id == included_apps_query.c.app_id
        )
    )
    if cursor_param:
        cursor_vals: Tuple = db.tuple_(*cursor_parts)
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

    if count_param:
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
        resp_apps.append(view_encoders.encode_app_model_object(app))

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
