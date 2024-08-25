from sqlalchemy import Select

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
