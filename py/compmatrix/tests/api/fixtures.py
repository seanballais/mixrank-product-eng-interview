import pytest

from compmatrix import db, model_encoders
from compmatrix.api import models
from compmatrix.tests.fixtures import app


@pytest.fixture
def test_apps(app):
    with app.app_context():
        pass


@pytest.fixture
def test_sdks(app):
    with app.app_context():
        # Test data taken from the provided data.db file.
        sdks = [
            models.SDK(name='PayPal', slug='paypal',
                       url='https://developer.paypal.com/webapps/developer'
                           '/docs/integration/mobile/mobile-sdk-overview/',
                       description='Accept credit cards and PayPal in your '
                                   'iOS app.'),
            models.SDK(name='card.io', slug='card-io',
                       url='https://www.card.io/',
                       description='Credit card scanning for mobile apps.'),
            models.SDK(name='Chartboost', slug='chartboost',
                       url='https://chartboost.com/',
                       description='ChartboostSDK for showing ads and '
                                   'more.')
        ]

        _add_model_objects_to_db(sdks)

        yield sdks

        _delete_model_objects_from_db(sdks)


def _add_model_objects_to_db(objects):
    for obj in objects:
        db.session.add(obj)

    # We're just flushing since we'd like to keep the model object data in
    # the database without expiring any objects.
    db.session.flush()


def _delete_model_objects_from_db(objects):
    for obj in objects:
        db.session.delete(obj)

    # We're just flushing since we'd like to keep the model object data in
    # the database without expiring any objects.
    db.session.flush()
