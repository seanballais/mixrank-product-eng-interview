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


def get_query_for_from_sdk_to_none(
        from_sdk_id: int,
        other_to_sdks_ids: list[int]
) -> CompoundSelect:
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

    return inner_query1.union(*unionable_queries)


def get_query_for_none_to_to_sdk(to_sdk_id: int,
                                 from_sdks_param: list[int]) -> Select:
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

    return query
