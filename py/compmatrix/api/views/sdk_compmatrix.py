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
