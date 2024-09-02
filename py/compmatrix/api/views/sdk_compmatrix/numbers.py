from collections import OrderedDict
from http import HTTPStatus

from flask import request
from sqlalchemy.sql.selectable import Select, CompoundSelect
from werkzeug.datastructures import MultiDict

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.api.views import messages, queries, checks
from compmatrix.utils import writing


def index():
    """
    Returns the number of apps that previously and currently have installed
    the SDKs specified in the parameters.

    We're sending back an HTTP 422 when responding to requests with
    incomplete parameters, since everything is alright, but we're missing
    some required content, which makes us unable to process stuff. Besides,
    HTTP 422 is already a part of HTTP since RFC 9110
    (https://datatracker.ietf.org/doc/html/rfc9110), which was published on
    June 2022, so no worries about non-standard practices.
    """
    resp: dict[str, object | list] = {}

    from_sdks_param: list[int] = [
        int(s) for s in request.args.getlist('from_sdks')
    ]
    to_sdks_param: list[int] = [
        int(s) for s in request.args.getlist('to_sdks')
    ]
    required_params: list[str] = ['from_sdks', 'to_sdks']

    client_params: MultiDict[str, str] = request.args

    _check_for_missing_params(resp, required_params, client_params)
    _check_for_unknown_params(resp, required_params, client_params)

    params_with_sdk_ids: OrderedDict = OrderedDict({
        'from_sdks': from_sdks_param,
        'to_sdks': to_sdks_param
    })
    checks.check_for_unknown_ids_in_params(resp, params_with_sdk_ids)

    if 'errors' in resp:
        return resp, HTTPStatus.UNPROCESSABLE_ENTITY

    num_sdks: int = db.session.query(models.SDK).count()

    number_values: list = []
    for from_sdk in from_sdks_param:
        from_sdk_id: int = from_sdk
        row_numbers: list = []

        # Get the numbers of apps from and to SDKs.
        for to_sdk in to_sdks_param:
            to_sdk_id: int = to_sdk
            count: int = db.session.execute(
                _get_count_query_for_from_to_sdks(from_sdk_id, to_sdk_id)
            ).scalar_one()
            row_numbers.append(count)

        # And we're gonna add a column for "(none)", since we're also gonna
        # count apps that used to have SDKs installed.
        count: int = db.session.execute(
            _get_count_query_for_from_sdk_to_none(from_sdk_id, to_sdks_param)
        ).scalar_one()
        row_numbers.append(count)

        number_values.append(row_numbers)

    if len(from_sdks_param) < num_sdks:
        # We're gonna have to add a row for SDKs that were not specified.
        row_numbers: list = []
        for to_sdk_id in to_sdks_param:
            count: int = db.session.execute(
                _get_count_query_for_none_to_to_sdk(to_sdk_id, from_sdks_param)
            ).scalar_one()
            row_numbers.append(count)

        # And then make a column for "(none)" again, since the apps that no
        # longer have SDKs installed are still counted.
        count: int = db.session.execute(
            _get_count_query_for_none_to_none(from_sdks_param, to_sdks_param)
        ).scalar_one()
        row_numbers.append(count)

        number_values.append(row_numbers)

    resp['data'] = {
        'numbers': number_values
    }

    return resp


def _check_for_missing_params(resp: dict[str, object | list],
                              required_params: list[str],
                              client_params: MultiDict[str, str]):
    missing_params: list[str] = [
        p for p in required_params if p not in client_params.keys()
    ]
    if missing_params:
        if 'errors' not in resp:
            resp['errors'] = []

        # We want `from_sdks` to go first instead of `to_sdks` for
        # aesthetics reasons. It just so happens that `from_sdks` will be
        # before `to_sdks`. So, sorting them after converting the collection
        # to a list seems like the right choice... for now. (DUN DUN DUN!!!)
        missing_params_list: list[str] = sorted(list(missing_params))
        resp['errors'].append({
            'message': messages.create_missing_params_message(
                missing_params_list
            ),
            'code': AnomalyCode.MISSING_FIELD,
            'parameters': list(missing_params)
        })


def _check_for_unknown_params(resp: dict[str, object | list],
                              known_params: list[str],
                              client_params: MultiDict[str, str]):
    # We need to preserve the order.
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


def _get_count_query_for_from_to_sdks(from_sdk_id: int,
                                      to_sdk_id: int) -> Select:
    query: Select = queries.get_query_for_from_to_sdks(from_sdk_id, to_sdk_id)
    return db.select(db.func.count('*')).select_from(query.subquery())


def _get_count_query_for_from_sdk_to_none(
        from_sdk_id: int,
        other_to_sdks_ids: list[int]
) -> Select:
    query: CompoundSelect = queries.get_query_for_from_sdk_to_none(
        from_sdk_id,
        other_to_sdks_ids)
    return db.select(db.func.count('*')).select_from(query.subquery())


def _get_count_query_for_none_to_to_sdk(
        to_sdk_id: int,
        other_from_sdks_param: list[int]
) -> Select:
    query: Select = queries.get_query_for_none_to_to_sdk(to_sdk_id,
                                                         other_from_sdks_param)
    return db.select(db.func.count('*')).select_from(query.subquery())


def _get_count_query_for_none_to_none(
        other_from_sdks_param: list[int],
        other_to_sdks_param: list[int]
) -> Select:
    query: Select = queries.get_query_for_none_to_none(other_from_sdks_param,
                                                       other_to_sdks_param)
    return db.select(db.func.count('*')).select_from(query.subquery())
