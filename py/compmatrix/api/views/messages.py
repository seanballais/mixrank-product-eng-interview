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


def create_misused_params_message(misused_params: list[str],
                                  tangled_params: list[str]):
    if len(misused_params) == 1:
        parameter_word: str = 'parameter'
    else:
        parameter_word: str = 'parameters'

    message: str = f'{parameter_word.capitalize()}, '

    oxfordify: bool = len(misused_params) != 2
    misused_params_list_str: str = writing.humanize_list(misused_params,
                                                         oxfordify,
                                                         True)
    dependee_params_list_str: str = writing.humanize_list(tangled_params,
                                                          oxfordify,
                                                          True)

    auxiliary_verb: str = 'is' if len(misused_params) == 1 else 'are'

    message += (
        f'{misused_params_list_str}, must only be specified if '
        f'the {dependee_params_list_str} {parameter_word} {auxiliary_verb} '
        'unspecified.'
    )

    return message
