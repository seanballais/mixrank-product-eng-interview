from compmatrix import model_encoders


def test_clean_model_object_dict():
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
    cleaned_model_dict = model_encoders.clean_model_object_dict(test_model)
    assert cleaned_model_dict == expected_model_dict
