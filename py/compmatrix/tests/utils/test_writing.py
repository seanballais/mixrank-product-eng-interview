from compmatrix.utils import writing


def test_humanize_list_str_0():
    assert writing.humanize_list([], False, False) == ''


def test_humanize_list_str_1():
    assert writing.humanize_list(['1'], False, False) == '1'


def test_humanize_list_str_2():
    assert writing.humanize_list(['1', '2'], False, False) == '1 and 2'


def test_humanize_list_str_3():
    strs = ['You\'d think me rude', 'but I would just stand', 'stare']
    expected_output = 'You\'d think me rude, but I would just stand and stare'
    assert writing.humanize_list(strs, False, False) == expected_output


def test_humanize_list_str_0_oxford_comma():
    assert writing.humanize_list([], True, False) == ''


def test_humanize_list_str_1_oxford_comma():
    assert writing.humanize_list(['1'], True, False) == '1'


def test_humanize_list_str_2_oxford_comma():
    assert writing.humanize_list(['1', '2'], True, False) == '1, and 2'


def test_humanize_list_str_3_oxford_comma():
    strs = ['You\'d think me rude', 'but I would just stand', 'stare']
    expected_output = 'You\'d think me rude, but I would just stand, and stare'
    assert writing.humanize_list(strs, True, False) == expected_output


def test_humanize_list_str_0_quoted():
    assert writing.humanize_list([], False, True) == ''


def test_humanize_list_str_1_quoted():
    assert writing.humanize_list(['1'], False, True) == '"1"'


def test_humanize_list_str_2_quoted():
    assert writing.humanize_list(['1', '2'], False, True) == '"1" and "2"'


def test_humanize_list_str_3_quoted():
    strs = ['You\'d think me rude', 'but I would just stand', 'stare']
    expected_output = (
        '"You\'d think me rude", "but I would just stand" '
        'and "stare"'
    )
    assert writing.humanize_list(strs, False, True) == expected_output


def test_humanize_list_str_0_oxford_comma_quoted():
    assert writing.humanize_list([], True, True) == ''


def test_humanize_list_str_1_oxford_comma_quoted():
    assert writing.humanize_list(['1'], True, True) == '"1"'


def test_humanize_list_str_2_oxford_comma_quoted():
    assert writing.humanize_list(['1', '2'], True, True) == '"1", and "2"'


def test_humanize_list_str_3_oxford_comma_quoted():
    strs = ['You\'d think me rude', 'but I would just stand', 'stare']
    expected_output = (
        '"You\'d think me rude", "but I would just stand", '
        'and "stare"'
    )
    assert writing.humanize_list(strs, True, True) == expected_output


def test_humanize_list_int_0():
    assert writing.humanize_list([], False, False) == ''


def test_humanize_list_int_1():
    assert writing.humanize_list([1], False, False) == '1'


def test_humanize_list_int_2():
    assert writing.humanize_list([1, 2], False, False) == '1 and 2'


def test_humanize_list_int_3():
    assert writing.humanize_list([1, 2, 3], False, False) == '1, 2 and 3'


def test_humanize_list_int_0_oxford_comma():
    assert writing.humanize_list([], True, False) == ''


def test_humanize_list_int_1_oxford_comma():
    assert writing.humanize_list([1], True, False) == '1'


def test_humanize_list_int_2_oxford_comma():
    assert writing.humanize_list([1, 2], True, False) == '1, and 2'


def test_humanize_list_int_3_oxford_comma():
    assert writing.humanize_list([1, 2, 3], True, False) == '1, 2, and 3'


def test_humanize_list_int_0_quoted():
    assert writing.humanize_list([], False, True) == ''


def test_humanize_list_int_1_quoted():
    assert writing.humanize_list([1], False, True) == '"1"'


def test_humanize_list_int_2_quoted():
    assert writing.humanize_list([1, 2], False, True) == '"1" and "2"'


def test_humanize_list_int_3_quoted():
    assert writing.humanize_list([1, 2, 3], False, True) == '"1", "2" and "3"'


def test_humanize_list_int_0_oxford_comma_quoted():
    assert writing.humanize_list([], True, True) == ''


def test_humanize_list_int_1_oxford_comma_quoted():
    assert writing.humanize_list([1], True, True) == '"1"'


def test_humanize_list_int_2_oxford_comma_quoted():
    assert writing.humanize_list([1, 2], True, True) == '"1", and "2"'


def test_humanize_list_int_3_oxford_comma_quoted():
    assert writing.humanize_list([1, 2, 3], True, True) == '"1", "2", and "3"'


def test_pluralize_word1():
    assert writing.pluralize_word('parameter') == 'parameters'
