import pytest

from compmatrix import db, model_encoders
from compmatrix.api import models
from compmatrix.tests.fixtures import app


@pytest.fixture
def sdk_records(app):
    with app.app_context():
        # Test data taken from the provided data.db file.
        sdk1 = models.SDK(name='PayPal', slug='paypal',
                          url='https://developer.paypal.com/webapps/developer'
                              '/docs/integration/mobile/mobile-sdk-overview/',
                          description='Accept credit cards and PayPal in your '
                                      'iOS app.')
        sdk2 = models.SDK(name='card.io', slug='card-io',
                          url='https://www.card.io/',
                          description='Credit card scanning for mobile apps.')
        sdk3 = models.SDK(name='Chartboost', slug='chartboost',
                          url='https://chartboost.com/',
                          description='ChartboostSDK for showing ads and '
                                      'more.')

        db.session.add(sdk1)
        db.session.add(sdk2)
        db.session.add(sdk3)

        # We're just flushing since we'd like to keep the model object data in
        # the database without expiring any objects.
        db.session.flush()

        yield [sdk1, sdk2, sdk3]

        db.session.delete(sdk1)
        db.session.delete(sdk2)
        db.session.delete(sdk3)
        db.session.flush()
