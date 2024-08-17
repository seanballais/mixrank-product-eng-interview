from http import HTTPStatus

from flask import request
from sqlalchemy.sql.selectable import Select, CompoundSelect

from compmatrix import db
from compmatrix.api import models
from compmatrix.api.views.codes import AnomalyCode


def numbers():
    # We're sending back an HTTP 422 when responding to requests with
    # incomplete parameters, since everything is alright, but we're missing
    # some required content, which makes us unable to process stuff. Besides,
    # HTTP 422 is already a part of HTTP since RFC 9110
    # (https://datatracker.ietf.org/doc/html/rfc9110), which was published on
    # June 2022, so no worries about non-standard practices.
    if 'from_sdks' not in request.args and 'to_sdks' not in request.args:
        return {
            'error': {
                'message': 'Required parameters, from_sdks and to_sdks, '
                           'are missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': [
                    'from_sdks',
                    'to_sdks'
                ]
            }
        }, HTTPStatus.UNPROCESSABLE_ENTITY

    if 'from_sdks' not in request.args:
        return {
            'error': {
                'message': 'Required parameter, from_sdks, is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['from_sdks']
            }
        }, HTTPStatus.UNPROCESSABLE_ENTITY

    if 'to_sdks' not in request.args:
        return {
            'error': {
                'message': 'Required parameter, to_sdks, is missing.',
                'code': AnomalyCode.MISSING_FIELD,
                'fields': ['to_sdks']
            }
        }, HTTPStatus.UNPROCESSABLE_ENTITY

    from_sdks_param: list[int] = [int(s) for s in
                                  request.args.getlist('from_sdks')]
    to_sdks_param: list[int] = [int(s) for s in
                                request.args.getlist('to_sdks')]

    num_sdks: int = db.session.query(models.SDK).count()

    numbers: list = []
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

        numbers.append(row_numbers)

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

        numbers.append(row_numbers)

    resp: dict[str, object] = {
        'data': {
            'numbers': numbers
        }
    }

    other_params: list[str] = [
        k for k in request.args.keys() if k != 'from_sdks' and k != 'to_sdks'
    ]
    if other_params:
        params_substr: str = ', '.join([f'"{p}"' for p in other_params[:-1]])
        params_substr += f', and "{other_params[-1]}"'
        warning_msg: str = f'Unrecognized parameters, {params_substr}.'
        resp['warning'] = {
            'message': warning_msg,
            'code': AnomalyCode.UNRECOGNIZED_FIELD,
            'fields': other_params
        }

    return resp


def apps():
    pass
