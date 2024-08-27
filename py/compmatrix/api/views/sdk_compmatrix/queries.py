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
