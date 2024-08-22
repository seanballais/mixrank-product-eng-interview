def humanize_list(l: list[object], use_oxford_comma: bool = True,
                  quote_items: bool = False) -> str:
    """
    Returns a simplified commaed string natural language version of the list
    of objects. Only supports English for now.

    Example:
        [1, 2, 3] -> '1, 2, and 3'
        [
            'never gonna give you up',
            'never gonna let you down',
            'never gonna run around',
            'hurt you
        ] -> 'never gonna give you up, never gonna let you down, '
             'never gonna run around, and hurt you'
    """
    surr_puncs: str = '"' if quote_items else ''

    if len(l) == 0:
        return ''
    elif len(l) == 1:
        return f'{surr_puncs}{str(l[0])}{surr_puncs}'

    text: str = ', '.join([f'{surr_puncs}{p}{surr_puncs}' for p in l[:-1]])
    text += (
        f'{"," if use_oxford_comma else ""} '
        f'and {surr_puncs}{l[-1]}{surr_puncs}'
    )
    return text


def pluralize_word(s: str) -> str:
    """
    Pluralizes a word. This will only check the last few characters. So, it
    will work best with a string with just one word. Additionally, we'll only
    be considering basic pluralizations for now. We'll add more cases as
    needed.
    """
    return f'{s.rstrip()}s'
