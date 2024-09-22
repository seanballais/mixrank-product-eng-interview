from sqlalchemy import Select, CompoundSelect

from compmatrix import db
from compmatrix.api import models


def get_query_for_from_to_sdks(from_sdk_id: int, to_sdk_id: int) -> Select:
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

    return query


def get_query_for_from_sdk_to_none(from_sdk_id: int,
                                   other_to_sdks_ids: list[int]) -> Select:
    inner_query1: Select = (
        db
        .select(models.AppSDK)
        .where(
            db.or_(
                db.and_(
                    models.AppSDK.sdk_id == from_sdk_id,
                    models.AppSDK.installed == False
                ),
                db.and_(
                    models.AppSDK.sdk_id.not_in(other_to_sdks_ids),
                    models.AppSDK.installed == True
                ),
            )
        )
        .group_by(models.AppSDK.app_id)
        .having(db.func.count(models.AppSDK.sdk_id) > 1)
    )

    # We're counting apps with no currently installed SDKs and one that used
    # to have the current row's "from" SDK installed but no longer does.
    no_sdk_apps_query: Select = (
        db
        .select(models.AppSDK)
        .group_by(models.AppSDK.app_id)
        .having(
            db.func.sum(
                db.case(
                    (models.AppSDK.installed, 1),
                    else_=0
                )
            ) == 0
        )
    )
    no_sdk_apps = db.aliased(models.AppSDK, no_sdk_apps_query.subquery())

    inner_query2: Select = (
        db
        .select(models.AppSDK)
        .select_from(models.AppSDK, no_sdk_apps)
        .where(
            db.and_(
                models.AppSDK.app_id == no_sdk_apps.app_id,
                models.AppSDK.sdk_id == from_sdk_id
            )
        )
    )

    unionable_queries: list[Select] = [inner_query2]

    if from_sdk_id not in other_to_sdks_ids:
        # The current SDK was not specified in the to_sdks parameter.
        # So, it's part of the "(none)" column. We need this separate
        # query since the prior query does not include apps that have
        # the current SDK installed but is not part of the to_sdks
        # parameters.
        inner_query3: Select = (
            db
            .select(models.AppSDK)
            .where(
                db.and_(
                    models.AppSDK.sdk_id == from_sdk_id,
                    models.AppSDK.installed == True
                )
            )
        )
        unionable_queries.append(inner_query3)

    query: CompoundSelect = inner_query1.union(*unionable_queries)
    return db.select(query.subquery()).group_by('app_id')


def get_query_for_none_to_to_sdk(to_sdk_id: int,
                                 other_from_sdks_param: list[int]) -> Select:
    # Since the `to_sdk` already has its own row in the matrix, we
    # shouldn't include them in the counting. Note that this condition
    # works because our query will initially include:
    #
    # 1) Rows where the SDK is not one that is not in the `other_from_sdks`
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
    if to_sdk_id in other_from_sdks_param:
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
                    models.AppSDK.sdk_id.not_in(other_from_sdks_param),
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

    return query


def get_query_for_none_to_none(other_from_sdks_param: list[int],
                               other_to_sdks_param: list[int]) -> Select:
    # Expected Rough Equivalent SQL Query:
    #
    # SELECT *
    # FROM (
    #     SELECT *
    #     FROM (
    #         SELECT *
    #         FROM app_sdk
    # 		  WHERE
    # 			  sdk_id NOT IN (from_sdks_param) AND installed = false
    # 	          OR sdk_id NOT IN (to_sdks_param) AND installed = true
    #         GROUP BY app_id
    # 	      HAVING
    #             COUNT(*) > 1
    #             AND SUM(CASE WHEN installed THEN 1 ELSE 0 END) > 0
    #     )
    #     UNION
    #     SELECT *
    #     FROM app_sdk
    #     WHERE
    #         sdk_id NOT IN (from_sdks_param + to_sdks_param)
    #         AND installed = true
    #     UNION
    #     SELECT *
    #     FROM app_sdk, (
    #         SELECT app_id
    #         FROM app_sdk
    #         GROUP BY app_id
    #         HAVING SUM(CASE WHEN installed THEN 1 ELSE 0 END) = 0
    #     ) AS filtered_apps
    #     WHERE
    #         app_sdk.app_id = filtered_apps.app_id
    #         AND app_sdk.sdk_id NOT IN (other_from_sdks_param)
    # )
    # GROUP BY app_id -- [^.^]
    #
    # First, get all the apps that had previous SDKs that are not part
    # of the `other_from_sdks_param` but are now using SDKs that are not part
    # of the `other_to_sdks_param`. This query will not ignore apps that only
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
                    models.AppSDK.sdk_id.not_in(other_from_sdks_param),
                    models.AppSDK.installed == False
                ),
                db.and_(
                    models.AppSDK.sdk_id.not_in(other_to_sdks_param),
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
        set(other_from_sdks_param + other_to_sdks_param)
    )
    # This query will get all apps that have SDKs that are not
    # specified in either `other_from_sdk_params` or `other_to_sdk_params`.
    # This will also capture apps that we already have in the previous
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

    # And now, we're counting apps with no currently installed SDKs and one
    # that used to have any SDK that does not have its own row in the
    # competitive matrix.
    no_sdk_apps_query: Select = (
        db
        .select(models.AppSDK)
        .group_by(models.AppSDK.app_id)
        .having(
            db.func.sum(
                db.case(
                    (models.AppSDK.installed, 1),
                    else_=0
                )
            ) == 0
        )
    )
    no_sdk_apps = db.aliased(models.AppSDK, no_sdk_apps_query.subquery())

    query3: Select = (
        db
        .select(models.AppSDK)
        .select_from(models.AppSDK, no_sdk_apps)
        .where(
            db.and_(
                models.AppSDK.app_id == no_sdk_apps.app_id,
                models.AppSDK.sdk_id.not_in(other_from_sdks_param)
            )
        )
    )

    query: CompoundSelect = query1.union(query2, query3)

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
    return db.select(query.subquery()).group_by('app_id')


def get_unknown_ids_in_list(ids: list[int]) -> list[int]:
    # As of August 2024, SQLAlchemy 2.0 does not have proper support for CTEs
    # for VALUES() rows. You would still need to use a SELECT FROM VALUES()
    # query inside the CTE just to make things work with SQLAlchemy. I'm also
    # having difficulty with such a query form in SQLite, where I am getting
    # syntax errors. So, we're just gonna use a raw SQL query for this one.
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
