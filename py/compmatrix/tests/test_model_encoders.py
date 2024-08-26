from datetime import datetime, timezone

from compmatrix import model_encoders
from compmatrix.model_encoders import ModelEncoderFilter


def test_encode_model_as_dict():
    test_model_id_value = 0
    test_model_description_value = 'This is a test model.'

    class TestModel:
        def __init__(self):
            # We're emulating SQLAlchemy's db.Model superclass here.
            self._sa_instance_state = 0
            self.id = test_model_id_value
            self.description = test_model_description_value

    test_model = TestModel()

    expected_model_dict = {
        'id': test_model_id_value,
        'description': test_model_description_value
    }
    cleaned_model_dict = model_encoders.encode_model_as_dict(test_model)
    assert cleaned_model_dict == expected_model_dict


def test_encode_model_as_dict_ignore_fields():
    test_model_id_value = 0
    test_model_description_value = 'This is a test model.'

    class TestModel:
        def __init__(self):
            self._sa_instance_state = 0
            self.id = test_model_id_value
            self.description = test_model_description_value
            self.ignored = 'Now this angel has flown away from meee'
            self.ignored2 = 'Thought that I had the strength to set her freee'
            self.do_not_include = 'Did what I did because I love her so'
            self.and_this_too = 'Will she ever find her way back home to me?'

    test_model = TestModel()

    expected_model_dict = {
        'id': test_model_id_value,
        'description': test_model_description_value
    }
    ignore_list = ['ignored', 'ignored2', 'do_not_include', 'and_this_too']
    cleaned_model_dict = model_encoders.encode_model_as_dict(
        test_model, ignored_fields=ignore_list)
    assert cleaned_model_dict == expected_model_dict


def test_encode_model_as_dict_apply_filters():
    test_model_id_value = 0
    test_model_title_value = 'Test Model'
    test_model_description_value = 'This is a test model.'

    class TestModel:
        def __init__(self):
            self._sa_instance_state = 0
            self.id = test_model_id_value
            self.title = test_model_title_value
            self.description = test_model_description_value

    test_model = TestModel()

    expected_model_dict = {
        'id': test_model_id_value + 10,
        'title': test_model_title_value.lower(),
        'description': test_model_description_value.lower()
    }
    filters = [
        ModelEncoderFilter('id', lambda x: x + 10),
        ModelEncoderFilter(['title', 'description'], lambda x: x.lower())
    ]
    cleaned_model_dict = model_encoders.encode_model_as_dict(test_model,
                                                             filters=filters)
    assert cleaned_model_dict == expected_model_dict


def test_encode_model_as_dict_ignore_fields_and_apply_filters():
    test_model_id_value = 0
    test_model_title_value = 'Test Model'
    test_model_description_value = 'This is a test model.'

    class TestModel:
        def __init__(self):
            self._sa_instance_state = 0
            self.id = test_model_id_value
            self.title = test_model_title_value
            self.description = test_model_description_value
            self.ignored = 'You are my fiirrreee'
            self.ignored2 = 'The one desiirrreee'
            self.do_not_include = 'Believe when I sayyyy'
            self.and_this_too = 'I want it thaaat wayy'

    test_model = TestModel()

    expected_model_dict = {
        'id': test_model_id_value + 10,
        'title': test_model_title_value.lower(),
        'description': test_model_description_value.lower()
    }
    ignore_list = ['ignored', 'ignored2', 'do_not_include', 'and_this_too']
    filters = [
        ModelEncoderFilter('id', lambda x: x + 10),
        ModelEncoderFilter(['title', 'description'], lambda x: x.lower())
    ]
    cleaned_model_dict = model_encoders.encode_model_as_dict(test_model,
                                                             ignore_list,
                                                             filters)
    assert cleaned_model_dict == expected_model_dict
