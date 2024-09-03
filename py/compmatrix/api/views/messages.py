from compmatrix.api.views.parameters import ParamPartnership
from compmatrix.api.views.sdk_compmatrix.apps import MisusedParamGroup
from compmatrix.utils import writing


def create_missing_params_message(missing_params: list[str]):
    message: str = 'Required '
    if len(missing_params) == 1:
        message += 'parameter, '
    else:
        message += 'parameters, '

    oxfordify: bool = len(missing_params) != 2
    missing_params_list_str: str = writing.humanize_list(missing_params,
                                                         oxfordify,
                                                         True)
    message += f'{missing_params_list_str}, '

    if len(missing_params) == 1:
        message += 'is '
    else:
        message += 'are '

    message += 'missing.'

    return message


def create_misused_params_message(misused_params_group: MisusedParamGroup,
                                  partner_params: dict[str, str]) -> str:
    params: list[str] = misused_params_group.parameters
    tangled_params: list[str] = []
    for param in params:
        tangled_params.append(partner_params[param])

    if len(params) == 1:
        parameter_word: str = 'parameter'
    else:
        parameter_word: str = 'parameters'

    message: str = f'{parameter_word.capitalize()}, '

    oxfordify: bool = len(params) != 2
    misused_params_list_str: str = writing.humanize_list(params,
                                                         oxfordify,
                                                         True)
    dependee_params_list_str: str = writing.humanize_list(tangled_params,
                                                          oxfordify,
                                                          True)

    auxiliary_verb: str = 'is' if len(params) == 1 else 'are'

    if misused_params_group.partnership == ParamPartnership.COUPLED:
        specification: str = 'specified'
    else:
        specification: str = 'unspecified'

    message += (
        f'{misused_params_list_str}, must only be specified if '
        f'the {dependee_params_list_str} {parameter_word} {auxiliary_verb} '
        f'{specification}'
    )

    if len(params) <= 1:
        message += '.'
    else:
        message += ', respectively.'

    return message


def create_wrong_valued_params_message(params: list[str]) -> str:
    int_params_set: set[str] = {
        'from_sdk',
        'other_from_sdks',
        'to_sdk',
        'other_to_sdks',
        'count'
    }

    int_params: list[str] = []
    message_parts: list[str] = []
    for param in params:
        if param in int_params_set:
            int_params.append(param)
        elif param == 'cursor':
            # No need to worry if params is empty since this part of the code
            # won't even run if it is empty.
            if len(params) == 1:
                sentence: str = ('The correct format is '
                                 '"<app name>;<app seller name>".')
            else:
                sentence: str = ('The correct format for the value of '
                                 '"cursor" is "<app name>;<app seller name>".')
            message_parts.append(sentence)
        elif param == 'direction':
            # No need to worry if params is empty since this part of the code
            # won't even run if it is empty.
            if len(params) == 1:
                sentence: str = ('It must only be either "previous" or '
                                 '"next".')
            else:
                sentence: str = ('The value of "direction" must only be '
                                 'either "previous" or "next".')
            message_parts.append(sentence)

    int_params_msg: str = _create_wrong_valued_int_params_message(int_params)
    if int_params_msg:
        message_parts.insert(0, int_params_msg)

    starter_message: str = _create_wrong_valued_params_starter_message(params)
    if starter_message:
        message_parts.insert(0, starter_message)

    return ' '.join(message_parts)


def create_unknown_params_message(params: list[str]) -> str:
    if len(params) == 1:
        message: str = 'Unrecognized parameter, '
    else:
        message: str = 'Unrecognized parameters, '

    oxfordify: bool = len(params) != 2
    message_substr: str = writing.humanize_list(params, oxfordify, True)
    message += f'{message_substr}.'

    return message


def create_unknown_ids_params_message(affected_params: list[str],
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


def _create_wrong_valued_int_params_message(params: list[str]) -> str | None:
    """
    Return a message about the parameters that requires an integer, but
    were not given such. Returns None if there are no wrong valued integer
    parameters.

    :param params: The list of parameters that require an integer, but were
                   not given such.
    :return: The generated message. Returns None if there are no wrong valued
             integer parameters.
    """
    if len(params) == 1:
        message: str = 'It must be an integer.'
    elif len(params) > 1:
        commafied_params: str = writing.humanize_list(params, True, True)
        message: str = f'Values of {commafied_params} must be integers.'
    else:
        message: None = None

    return message


def _create_wrong_valued_params_starter_message(params: list[str]):
    if len(params) == 1:
        message: str = 'Parameter, '
    else:
        message: str = 'Parameters, '

    oxfordify: bool = len(params) != 2
    params_list_str: str = writing.humanize_list(params, oxfordify, True)
    message += f'{params_list_str}, '

    if len(params) == 1:
        message += 'has an invalid value.'
    else:
        message += 'have invalid values.'

    return message
