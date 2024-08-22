import json
from collections import OrderedDict
from http import HTTPStatus

from flask import request
from sqlalchemy.sql.selectable import Select, CompoundSelect
from werkzeug.datastructures import MultiDict

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views.codes import AnomalyCode
from compmatrix.utils import writing


def numbers():
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
    _check_for_unknown_ids_in_params(resp,
                                     OrderedDict({
                                         'from_sdks': from_sdks_param,
                                         'to_sdks': to_sdks_param
                                     }))

    if 'errors' in resp:
        return resp, HTTPStatus.UNPROCESSABLE_ENTITY

    num_sdks: int = db.session.query(models.SDK).count()

    number_values: list = []
    for from_sdk in from_sdks_param:
        from_sdk_id: int = from_sdk
        row_numbers: list = []
        for to_sdk in to_sdks_param:
            to_sdk_id: int = to_sdk
            if from_sdk_id == to_sdk_id:
                sdk_id: int = from_sdk_id  # Can be `to_sdk` too if you prefer.
                query: Select = (
                    db
                    .select(models.AppSDK)
                    .where(
                        db.and_(
                            models.AppSDK.sdk_id == sdk_id,
                            models.AppSDK.installed == True
                        )
                    )
                    .group_by(models.AppSDK.app_id)
                )
                query: Select = db.select(db.func.count('*')).select_from(
                    query.subquery())
            else:
                query: Select = (
                    db
                    .select(models.AppSDK)
                    .where(
                        db.or_(
                            db.and_(
                                models.AppSDK.sdk_id == from_sdk_id,
                                models.AppSDK.installed == False
                            ),
                            db.and_(
                                models.AppSDK.sdk_id == to_sdk_id,
                                models.AppSDK.installed == True
                            ),
                        )
                    )
                    .group_by(models.AppSDK.app_id)
                    .having(db.func.count(models.AppSDK.sdk_id) > 1)
                )
                query: Select = db.select(db.func.count('*')).select_from(
                    query.subquery())
            count: int = db.session.execute(query).scalar_one()
            row_numbers.append(count)

        if len(to_sdks_param) < num_sdks:
            # We're gonna have to add a column for "(none)".
            query: Select = (
                db
                .select(models.AppSDK)
                .where(
                    db.or_(
                        db.and_(
                            models.AppSDK.sdk_id == from_sdk_id,
                            models.AppSDK.installed == False
                        ),
                        db.and_(
                            models.AppSDK.sdk_id.not_in(to_sdks_param),
                            models.AppSDK.installed == True
                        ),
                    )
                )
                .group_by(models.AppSDK.app_id)
                .having(db.func.count(models.AppSDK.sdk_id) > 1)
            )
            if from_sdk_id not in to_sdks_param:
                # The current SDK was not specified in the to_sdks parameter.
                # So, it's part of the "(none)" column. We need this separate
                # query since the prior query does not include apps that have
                # the current SDK installed but is not part of the to_sdks
                # parameters.
                subquery: Select = (
                    db
                    .select(models.AppSDK)
                    .where(
                        db.and_(
                            models.AppSDK.sdk_id == from_sdk_id,
                            models.AppSDK.installed == True
                        )
                    )
                )
                query: CompoundSelect = query.union(subquery)

            query: Select = db.select(db.func.count('*')).select_from(
                query.subquery())
            count: int = db.session.execute(query).scalar_one()
            row_numbers.append(count)

        number_values.append(row_numbers)

    if len(from_sdks_param) < num_sdks:
        # We're gonna have to add a row for "(none)".
        row_numbers: list = []
        for to_sdk_id in to_sdks_param:
            # Since the `to_sdk` already has its own row in the matrix, we
            # shouldn't include them in the counting. Note that this condition
            # works because our query will initially include:
            #
            # 1) Rows where the SDK is not one that is not in the `from_sdks`
            #    and also currently not installed.
            # 2) Rows where the SDK is the one referred to by `to_sdk_id`
            #    and also installed.
            #
            # Afterwards, the query will group the rows by app ID. We'll refer
            # to these groups as "app groups". Some app groups will have rows
            # that have their `installed` column set to false (i.e. the app has
            # no SDK installed currently). These groups will be ignored. For
            # the app groups that won't be ignored, in most cases, there would
            # be with at least two rows if an app has had at least two SDKs
            # installed with one those SDKs current installed. However, if an
            # app has only one SDK that is also currently installed (note that
            # we are ignoring apps with no SDKs installed), then the app group
            # for that app will only have one row.
            if to_sdk_id in from_sdks_param:
                # We should not include apps where it only has one SDK
                # currently installed and that SDK is the one being referred to
                # by `to_sdk_id`, because they should be counted in the row
                # in the competitive matrix dedicated to the SDK.
                having_count_query = db.func.count('*') > 1
            else:
                # The SDK being to referred to by `to_sdk_id` does not have its
                # own row in the competitive matrix. So, it belongs to the
                # "(none)" column, and we should include it in our count even
                # though it only has one row (which, as mentioned previously,
                # happens when an app only has one SDK that is also currently
                # installed).
                having_count_query = db.func.count('*') >= 1

            query: Select = (
                db
                .select(models.AppSDK)
                .where(
                    db.or_(
                        db.and_(
                            models.AppSDK.sdk_id.not_in(from_sdks_param),
                            models.AppSDK.installed == False
                        ),
                        db.and_(
                            models.AppSDK.sdk_id == to_sdk_id,
                            models.AppSDK.installed == True
                        ),
                    )
                )
                .group_by(models.AppSDK.app_id)
                .having(
                    db.and_(
                        having_count_query,
                        # Ensures that there is an SDK installed within
                        # the group.
                        db.func.sum(
                            db.case(
                                (models.AppSDK.installed, 1),
                                else_=0
                            )
                        ) > 0
                    )
                )
            )

            query: Select = db.select(
                db.func.count('*')
            ).select_from(
                query.subquery()
            )
            count: int = db.session.execute(query).scalar_one()
            row_numbers.append(count)

        if len(to_sdks_param) < num_sdks:
            # Expected Rough Equivalent SQL Query:
            #
            # SELECT COUNT(*)
            # FROM (
            # 	SELECT *
            # 	FROM (
            # 		SELECT *
            # 		FROM (
            # 			SELECT *
            # 			FROM app_sdk
            # 			WHERE
            # 				sdk_id NOT IN (from_sdks_param)
            # 	    			AND installed = false
            # 	      		OR
            # 				sdk_id NOT IN (to_sdks_param) AND installed = true
            # 			GROUP BY app_id
            # 			HAVING COUNT(*) > 1
            # 	   		    AND SUM(CASE WHEN installed THEN 1 ELSE 0 END) > 0
            # 		)
            # 		UNION
            # 		SELECT *
            # 		FROM app_sdk
            # 		WHERE
            # 			sdk_id NOT IN (from_sdks_param + to_sdks_param)
            # 	   		    AND installed = true
            # 	)
            # 	GROUP BY app_id -- [^.^]
            # )
            #
            # First, get all the apps that had previous SDKs that are not part
            # of the `from_sdks_param` but are now using SDKs that are not part
            # of the `to_sdks_param`. This query will not ignore apps that only
            # have one SDK installed. The way our query is formed initially
            # includes apps with only one SDK installed with that SDK having
            # its own row in the competitive matrix. These only use one row.
            # So, later in the query, they are removed. But this also removes
            # apps that also have one SDK installed currently and throughout
            # its lifetime but does not have its own row in the matrix. The
            # next query lets us get these "lost" rows again.
            query1: Select = (
                db
                .select(models.AppSDK)
                .where(
                    db.or_(
                        db.and_(
                            models.AppSDK.sdk_id.not_in(from_sdks_param),
                            models.AppSDK.installed == False
                        ),
                        db.and_(
                            models.AppSDK.sdk_id.not_in(to_sdks_param),
                            models.AppSDK.installed == True
                        )
                    )
                )
                .group_by(models.AppSDK.app_id)
                .having(
                    db.and_(
                        db.func.count('*') > 1,
                        db.func.sum(
                            db.case(
                                (models.AppSDK.installed, 1),
                                else_=0
                            )
                        ) > 0
                    )
                )
            )
            query1: CompoundSelect = db.select(query1.subquery())

            all_sdks_specified: list[int] = list(
                set(from_sdks_param + to_sdks_param)
            )
            # This query will get all apps that have SDKs that are not
            # specified in either `from_sdk_params` or `to_sdk_params`. This
            # will also capture apps that we already have in the previous
            # query. We'll remove duplicates later after a union.
            query2: Select = (
                db
                .select(models.AppSDK)
                .where(
                    db.and_(
                        models.AppSDK.sdk_id.not_in(all_sdks_specified),
                        models.AppSDK.installed == True
                    )
                )
            )

            # Union the two queries so we get the apps with SDKs that are not
            # specified in the competitive matrix.
            query: CompoundSelect = query1.union(query2)

            # Merge the rows that share the same app ID with a `GROUP BY`.
            # We're using 'app_id' for the GROUP BY statement instead of
            # `models.AppSDK.app_id` because the latter will cause SQLAlchemy
            # to generate `GROUP BY app_sdk.app_id`. This will cause the entire
            # query to fail since we didn't reference `app_sdk` in this level
            # of the query. (See the SQL query above for reference. This GROUP
            # BY statement is marked by a "[^.^]" label in a comment. Kawaiii).
            # Fortunately, the query at this will have an `app_id` column,
            # resulting from the effects of the innermost subqueries. So, we'll
            # just reference the column directly with 'app_id'.
            query: Select = db.select(query.subquery()).group_by('app_id')

            # Now, get the count.
            query = db.select(db.func.count('*')).select_from(query.subquery())
            count: int = db.session.execute(query).scalar_one()
            row_numbers.append(count)

        number_values.append(row_numbers)

    resp['data'] = {
        'numbers': number_values
    }

    return resp


def apps():
    pass


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
            'message': _create_missing_params_message(missing_params_list),
            'code': AnomalyCode.MISSING_FIELD,
            'fields': list(missing_params)
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

        if len(unknown_params) == 1:
            message: str = 'Unrecognized parameter, '
        else:
            message: str = 'Unrecognized parameters, '

        oxfordify: bool = len(unknown_params) != 2
        message_substr: str = writing.humanize_list(unknown_params,
                                                    oxfordify,
                                                    True)
        message += f'{message_substr}.'
        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.UNRECOGNIZED_FIELD,
            'fields': unknown_params
        })


def _check_for_unknown_ids_in_params(resp: dict[str, object | list],
                                     params: OrderedDict[str, list[int]]):
    # We need the `params` parameters to be in order. Although insertion order
    # of dictionaries since Python 3.7 is preserved, we opted to use
    # OrderedDict here to properly communicate that we're expecting the
    # parameter to have its key-value pairs in a specific order.
    params_with_unknown_ids: list[str] = []
    unknown_ids_per_param: dict[str, list[int]] = {}
    for name, value in params.items():
        unknown_ids: list[int] = _check_for_unknown_ids_in_param(value)
        if unknown_ids:
            params_with_unknown_ids.append(name)
            unknown_ids_per_param[name] = unknown_ids

    if params_with_unknown_ids:
        if 'errors' not in resp:
            resp['errors'] = []

        num_unknown_ids: int = sum(
            [len(unknown_ids)
             for unknown_ids in unknown_ids_per_param.values()]
        )
        message: str = _create_unknown_ids_params_message(
            params_with_unknown_ids, num_unknown_ids)
        resp['errors'].append({
            'message': message,
            'code': AnomalyCode.UNKNOWN_IDS,
            'fields': params_with_unknown_ids,
            'diagnostics': unknown_ids_per_param
        })


def _check_for_unknown_ids_in_param(ids: list[int]) -> list[int]:
    query = db.text(
        'WITH id_list(id) AS :ids '
        'SELECT id '
        'FROM id_list '
        'WHERE NOT EXISTS ('
        '    SELECT * '
        '    FROM sdk '
        '    WHERE sdk.id = id_list.id'
        ')'
    )
    query = query.bindparams(db.bindparam('ids', expanding=True))
    params: dict = {
        'ids': [(_id,) for _id in ids]
    }
    unknown_id_results: list = db.session.execute(query, params).fetchall()
    unknown_ids: list[int] = [result[0] for result in unknown_id_results]
    return unknown_ids


def _create_missing_params_message(missing_params: list[str]):
    message: str = 'Required '
    if len(missing_params) == 1:
        message += 'parameter, '
    else:
        message += 'parameters, '

    oxfordify: bool = len(missing_params) != 2
    missing_params_list_str: str = writing.humanize_list(
        missing_params, oxfordify, True
    )
    message += f'{missing_params_list_str}, '

    if len(missing_params) == 1:
        message += 'is '
    else:
        message += 'are '

    message += 'missing.'

    return message


def _create_unknown_ids_params_message(affected_params: list[str],
                                       num_unknown_ids: int) -> str:
    oxfordify: bool = len(affected_params) != 2
    message: str = writing.humanize_list(affected_params, oxfordify, True)

    # NOTE: A message with 'Parameters, ":param1" and ":param2", have an ID
    #       that does...' will only happen if we have two parameters with
    #       unknown IDs but only having one unknown ID in actuality. However,
    #       this is unlikely to happen.
    if len(affected_params) == 1:
        message = f'Parameter, {message}, has '
    else:
        message = f'Parameters, {message}, have '

    if num_unknown_ids == 1:
        message += 'an ID that does '
    else:
        message += 'IDs that do '

    message += 'not refer to an SDK.'

    return message
