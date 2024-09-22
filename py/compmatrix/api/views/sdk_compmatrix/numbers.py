import dataclasses
from collections import OrderedDict
from http import HTTPStatus

from flask import request
from sqlalchemy.sql.selectable import Select
from werkzeug.datastructures import MultiDict

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views import queries, checks, responses


@dataclasses.dataclass
class SDKParamValues:
    valid: list[int]
    invalid: list[object]


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
    client_params: MultiDict[str, str] = request.args
    resp: dict[str, object | list] = {}
    known_params: list[str] = ['from_sdks', 'to_sdks']

    from_sdks_vals: SDKParamValues = _get_sdk_param_values('from_sdks',
                                                           client_params)
    to_sdks_vals: SDKParamValues = _get_sdk_param_values('to_sdks',
                                                         client_params)

    checks.check_for_unknown_params(resp, known_params, client_params)

    if from_sdks_vals.invalid or to_sdks_vals.invalid:
        # TODO: We should be able to know the number of values a parameter has
        #       so that we can send out better messages.
        wrong_valued_params: list[str] = []
        diagnostics: dict[str, list[object]] = {}
        if from_sdks_vals.invalid:
            wrong_valued_params.append('from_sdks')
            diagnostics['from_sdks'] = from_sdks_vals.invalid

        if to_sdks_vals.invalid:
            wrong_valued_params.append('to_sdks')
            diagnostics['to_sdks'] = to_sdks_vals.invalid

        responses.generate_wrong_valued_params_resp_error(resp,
                                                          wrong_valued_params)

        # Temporarily to do it here, while the other endpoint (/apps) is not
        # expecting a diagnostics field yet. In the future, we should put a
        # diagnostics field in the other endpoint.
        resp['errors'][-1]['diagnostics'] = diagnostics

    params_with_sdk_ids: OrderedDict = OrderedDict({
        'from_sdks': from_sdks_vals.valid,
        'to_sdks': to_sdks_vals.valid
    })
    checks.check_for_unknown_ids_in_params(resp, params_with_sdk_ids)

    if 'errors' in resp:
        return resp, HTTPStatus.UNPROCESSABLE_ENTITY

    num_sdks: int = db.session.query(models.SDK).count()

    number_values: list = []
    from_sdks = from_sdks_vals.valid
    to_sdks = to_sdks_vals.valid
    for from_sdk in from_sdks:
        from_sdk_id: int = from_sdk
        row_numbers: list = []

        # Get the numbers of apps from and to SDKs.
        for to_sdk in to_sdks:
            to_sdk_id: int = to_sdk
            count: int = db.session.execute(
                _get_count_query_for_from_to_sdks(from_sdk_id, to_sdk_id)
            ).scalar_one()
            row_numbers.append(count)

        # And we're gonna add a column for "(none)", since we're also gonna
        # count apps that used to have SDKs installed.
        count: int = db.session.execute(
            _get_count_query_for_from_sdk_to_none(from_sdk_id, to_sdks)
        ).scalar_one()
        row_numbers.append(count)

        number_values.append(row_numbers)

    # We're gonna have to add a row for apps with no SDKs and whose SDKs that
    # were not specified.
    row_numbers: list = []
    for to_sdk_id in to_sdks:
        count: int = db.session.execute(
            _get_count_query_for_none_to_to_sdk(to_sdk_id, from_sdks)
        ).scalar_one()
        row_numbers.append(count)

    # And then make a column for "(none)" again, since the apps that no
    # longer have SDKs installed are still counted.
    count: int = db.session.execute(
        _get_count_query_for_none_to_none(from_sdks, to_sdks)
    ).scalar_one()
    row_numbers.append(count)

    number_values.append(row_numbers)

    resp['data'] = {
        'numbers': number_values
    }

    return resp


def _get_sdk_param_values(
        param_name: str,
        client_params: MultiDict[str, str]
) -> SDKParamValues:
    sdk_params: list[int] = []
    invalid_values: list[object] = []
    if param_name in client_params and client_params.get(param_name) != '':
        for s in client_params.getlist(param_name):
            try:
                sdk: int = int(s)
                sdk_params.append(sdk)
            except ValueError:
                invalid_values.append(s)

    return SDKParamValues(sdk_params, invalid_values)


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
