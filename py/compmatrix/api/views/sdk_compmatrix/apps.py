import dataclasses
from collections import OrderedDict
from http import HTTPStatus

from flask import request
from flask_sqlalchemy.query import Query
from sqlalchemy import Subquery, Tuple, Select
from werkzeug.datastructures import MultiDict

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views import messages, queries, checks, responses
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.api.views import view_encoders
from compmatrix.api.views.parameters import ParamPartnership


@dataclasses.dataclass
class SDKParamPair:
    target_sdk: int | None
    other_sdks: list[int]


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
    required_params: list[str] = ['count']
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

    checks.check_for_missing_params(resp, required_params, client_params)
    checks.check_for_unknown_params(resp, known_params, client_params)

    misused_param_groups: list[MisusedParamGroup] = []
    wrong_valued_params: list[str] = []

    misused_sdk_params: list[str] = []

    raw_from_sdks_params = _get_paired_sdk_params('from_sdk',
                                                  'other_from_sdks',
                                                  client_params,
                                                  params_with_sdk_ids_to_check,
                                                  wrong_valued_params,
                                                  misused_sdk_params)
    from_sdk_param: int | None = raw_from_sdks_params.target_sdk
    other_from_sdks_param: list[int] = raw_from_sdks_params.other_sdks

    raw_to_sdks_params = _get_paired_sdk_params('to_sdk',
                                                'other_to_sdks',
                                                client_params,
                                                params_with_sdk_ids_to_check,
                                                wrong_valued_params,
                                                misused_sdk_params)
    to_sdk_param: int | None = raw_to_sdks_params.target_sdk
    other_to_sdks_param: list[int] = raw_to_sdks_params.other_sdks

    if misused_sdk_params:
        misused_param_groups.append(
            MisusedParamGroup(misused_sdk_params, ParamPartnership.INVERSE))

    count_param: int | None = _get_count_param_value(client_params,
                                                     wrong_valued_params)
    cursor_param: str | None = client_params.get('cursor')
    cursor_parts: list[str] | None = _get_cursor_parts(cursor_param,
                                                       wrong_valued_params)
    direction_param: str | None = _get_direction_param(client_params,
                                                       wrong_valued_params)
    _validate_cursor_and_direction_params(cursor_param,
                                          direction_param,
                                          resp,
                                          client_params,
                                          misused_param_groups)

    if wrong_valued_params:
        responses.generate_wrong_valued_params_resp_error(resp,
                                                          wrong_valued_params)

    if params_with_sdk_ids_to_check:
        checks.check_for_unknown_ids_in_params(resp,
                                               params_with_sdk_ids_to_check)

    if misused_param_groups:
        _generate_misused_params_resp_error(resp, misused_param_groups,
                                            partner_params)

    if 'errors' in resp:
        return resp, HTTPStatus.UNPROCESSABLE_ENTITY

    # We finally got all the parameter values. It's time to query our database
    # for it.
    if from_sdk_param is None and to_sdk_param is None:
        included_apps_query: Select = queries.get_query_for_none_to_none(
            other_from_sdks_param, other_to_sdks_param
        )
    elif from_sdk_param is None and to_sdk_param is not None:
        included_apps_query: Select = queries.get_query_for_none_to_to_sdk(
            to_sdk_param, other_from_sdks_param)
    elif to_sdk_param is None and from_sdk_param is not None:
        included_apps_query: Select = (
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


def _get_paired_sdk_params(target_sdk_param: str,
                           other_sdks_param: str,
                           client_params: MultiDict[str, str],
                           params_with_ids_to_check: OrderedDict,
                           wrong_valued_params: list[str],
                           misused_sdk_params: list[str]) -> SDKParamPair:
    target_sdk: int | None = None
    other_sdks: list[int] = []
    is_target_sdk_specified = (target_sdk_param in client_params
                               and client_params.get(target_sdk_param) != '')
    if is_target_sdk_specified:
        try:
            target_sdk = int(client_params.get(target_sdk_param))
            params_with_ids_to_check[target_sdk_param] = target_sdk
        except ValueError:
            wrong_valued_params.append(target_sdk_param)

        if other_sdks_param in client_params:
            misused_sdk_params.append(other_sdks_param)

    # We need to check the values of other_from_sdks even if they are not
    # supposed to be specified.
    has_bad_val: bool = False
    for s in client_params.getlist(other_sdks_param):
        if s != '':
            try:
                sdk: int = int(s)
                other_sdks.append(sdk)
            except ValueError:
                has_bad_val = True

    if has_bad_val:
        wrong_valued_params.append(other_sdks_param)

    params_with_ids_to_check[other_sdks_param] = other_sdks

    return SDKParamPair(target_sdk, other_sdks)


def _get_count_param_value(client_params: MultiDict[str, str],
                           wrong_valued_params: list[str]) -> int | None:
    raw_count_value: str | None = client_params.get('count')
    if raw_count_value:
        try:
            count_param = int(raw_count_value)
            return count_param
        except ValueError:
            wrong_valued_params.append('count')

    return None


def _get_cursor_parts(cursor_param: str | None,
                      wrong_valued_params: list[str]) -> list[str]:
    if cursor_param:
        cursor_parts: list[str] = cursor_param.split(';')
        if len(cursor_parts) != 2:
            wrong_valued_params.append('cursor')
    else:
        cursor_parts: list[str] = []

    return cursor_parts


def _get_direction_param(client_params: MultiDict[str, str],
                         wrong_valued_params: list[str]) -> str | None:
    if 'direction' in client_params:
        direction_param: str = client_params.get('direction')
        if direction_param != "previous" and direction_param != "next":
            wrong_valued_params.append('direction')
    else:
        direction_param: None = None

    return direction_param


def _generate_misused_params_resp_error(resp: dict[str, object | list],
                                        param_groups: list[MisusedParamGroup],
                                        partner_params: dict[str, str]):
    if param_groups:
        if 'errors' not in resp:
            resp['errors'] = []

        message_parts: list[str] = []
        for group in param_groups:
            message_parts.append(
                messages.create_misused_params_message(group, partner_params))

        message: str = ' '.join(message_parts)

        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.MISUSED_PARAMETER,
            'parameters': [
                p for g in param_groups for p in g.parameters
            ]
        })


def _validate_cursor_and_direction_params(
        cursor_param: str | None,
        direction_param: str | None,
        resp: dict[str, object | list],
        client_params: MultiDict[str, str],
        misused_param_groups: list[MisusedParamGroup]):
    if cursor_param:
        if 'direction' not in client_params:
            if 'errors' not in resp:
                resp['errors'] = []

            missing_param: list[str] = ['direction']
            message: str = messages.create_missing_params_message(
                missing_param)
            message = (
                f'{message} It is required when the "cursor" parameter '
                'is specified.'
            )
            resp['errors'].append({
                'message': message,
                'code': AnomalyCode.MISSING_FIELD,
                'parameters': list(missing_param)
            })
    elif direction_param is not None:
        # direction parameter specified even if cursor was not.
        misused_param_groups.append(
            MisusedParamGroup(['direction'], ParamPartnership.COUPLED))


def _create_cursor_from_app(app: models.App) -> str:
    return f'{app.name};{app.seller_name}'
