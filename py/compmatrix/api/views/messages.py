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
