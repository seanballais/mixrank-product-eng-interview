from collections import OrderedDict
from http import HTTPStatus

from flask import request
from sqlalchemy.sql.selectable import Select, CompoundSelect
from werkzeug.datastructures import MultiDict

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views import queries, checks


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

    # TODO: Validate these params.
    from_sdks_param: list[int] = [
        int(s) for s in request.args.getlist('from_sdks')
    ]
    to_sdks_param: list[int] = [
        int(s) for s in request.args.getlist('to_sdks')
    ]
    known_params: list[str] = ['from_sdks', 'to_sdks']

    client_params: MultiDict[str, str] = request.args

    checks.check_for_unknown_params(resp, known_params, client_params)

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


def _get_count_query_for_from_to_sdks(from_sdk_id: int,
                                      to_sdk_id: int) -> Select:
    query: Select = queries.get_query_for_from_to_sdks(from_sdk_id, to_sdk_id)
    return db.select(db.func.count('*')).select_from(query.subquery())


def _get_count_query_for_from_sdk_to_none(
        from_sdk_id: int,
        other_to_sdks_ids: list[int]
) -> Select:
    query: Select = queries.get_query_for_from_sdk_to_none(
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
