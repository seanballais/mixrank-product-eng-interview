from datetime import datetime

import pytest

from compmatrix import db
from compmatrix.api import models
from compmatrix.tests.fixtures import app


@pytest.fixture
def test_apps(app):
    with app.app_context():
        apps = [
            models.App(name='Clash of Clans',
                       company_url='',
                       release_date=_timestamp_to_datetime(
                           '2012-06-14 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is4-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/14/06/11/'
                                         '140611bf-46d8-9acc-6ad0-'
                                         '54d4b41c462c/source/100x100bb.jpg',
                       seller_name='Supercell Oy',
                       five_star_ratings=9688107,
                       four_star_ratings=1188416,
                       three_star_ratings=518847,
                       two_star_ratings=278717,
                       one_star_ratings=472375),
            models.App(name='Roblox',
                       company_url='http://www.roblox.com/',
                       release_date=_timestamp_to_datetime(
                           '2011-05-26 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is1-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/46/52/e0/'
                                         '4652e0c7-ce94-39ac-11a3-'
                                         'c6c1efa999d9/source/100x100bb.jpg',
                       seller_name='Roblox Corporation',
                       five_star_ratings=3400713,
                       four_star_ratings=372076,
                       three_star_ratings=144039,
                       two_star_ratings=81347,
                       one_star_ratings=199537),
            models.App(name='Candy Crush Saga',
                       company_url='http://candycrushsaga.com/',
                       release_date=_timestamp_to_datetime(
                           '2012-10-19 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is1-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/25/7a/95/'
                                         '257a95b9-9f3b-e07d-04f9-'
                                         '40890d4f8f31/source/100x100bb.jpg',
                       seller_name='King.com Limited',
                       five_star_ratings=4639681,
                       four_star_ratings=1127279,
                       three_star_ratings=360126,
                       two_star_ratings=136377,
                       one_star_ratings=229664),
            models.App(name='Hay Day',
                       company_url='',
                       release_date=_timestamp_to_datetime(
                           '2012-05-04 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is5-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/dd/f4/99/'
                                         'ddf49901-6dcb-35c7-e6ab-'
                                         'da383080606e/source/100x100bb.jpg',
                       seller_name='Supercell Oy',
                       five_star_ratings=2961454,
                       four_star_ratings=518310,
                       three_star_ratings=245958,
                       two_star_ratings=124342,
                       one_star_ratings=166093),
            models.App(name='8 Ball Pool™',
                       company_url='https://www.miniclip.com/',
                       release_date=_timestamp_to_datetime(
                           '2013-02-23 00:12:47'),
                       genre_id=6014,
                       artwork_large_url='https://is3-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/72/71/da/'
                                         '7271daf2-4f08-19b5-0fa9-'
                                         '91d733c00726/source/100x100bb.jpg',
                       seller_name='Miniclip SA',
                       five_star_ratings=4390350,
                       four_star_ratings=602842,
                       three_star_ratings=191890,
                       two_star_ratings=60333,
                       one_star_ratings=121161),
            models.App(name='PUBG MOBILE - 2nd Anniversary',
                       company_url='',
                       release_date=_timestamp_to_datetime(
                           '2018-03-17 02:52:55'),
                       genre_id=6014,
                       artwork_large_url='https://is1-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/13/67/1a/'
                                         '13671a17-87b7-e237-7278-'
                                         '8d5f9fccfe39/source/100x100bb.jpg',
                       seller_name='Tencent Mobile International Limited',
                       five_star_ratings=2745367,
                       four_star_ratings=304056,
                       three_star_ratings=158093,
                       two_star_ratings=112031,
                       one_star_ratings=290979),
            models.App(name='Subway Surfers',
                       company_url='http://www.sybogames.com/',
                       release_date=_timestamp_to_datetime(
                           '2012-05-24 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is4-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/77/8d/05/'
                                         '778d0578-fddf-4885-27d4-'
                                         '0b8585a5a0e6/source/100x100bb.jpg',
                       seller_name='Sybo Games ApS',
                       five_star_ratings=1988926,
                       four_star_ratings=362806,
                       three_star_ratings=172666,
                       two_star_ratings=99547,
                       one_star_ratings=130226),
            models.App(name='Dragon City Mobile',
                       company_url='https://www.dragoncitygame.com/',
                       release_date=_timestamp_to_datetime(
                           '2013-01-09 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is1-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/93/e5/d7/'
                                         '93e5d7df-e0fc-7fc2-3fb3-'
                                         '8a31db4e8c4f/source/100x100bb.jpg',
                       seller_name='Socialpoint',
                       five_star_ratings=1352299,
                       four_star_ratings=183487,
                       three_star_ratings=67943,
                       two_star_ratings=28642,
                       one_star_ratings=46720),
            models.App(name='Township',
                       company_url='https://www.playrix.com/township/'
                                   'index.html',
                       release_date=_timestamp_to_datetime(
                           '2013-06-22 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is2-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/d0/51/45/'
                                         'd05145fc-9e50-ef23-e6dd-'
                                         'cec273f1d775/source/100x100bb.jpg',
                       seller_name='PLR Worldwide Sales Limited',
                       five_star_ratings=1855078,
                       four_star_ratings=269763,
                       three_star_ratings=95801,
                       two_star_ratings=38346,
                       one_star_ratings=50488),
            models.App(name='Asphalt 8: Airborne',
                       company_url='http://www.gameloft.com',
                       release_date=_timestamp_to_datetime(
                           '2013-08-14 00:42:26'),
                       genre_id=6014,
                       artwork_large_url='https://is3-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/04/77/7b/'
                                         '04777b70-4da1-27d8-e31a-'
                                         '87fff7c37a74/source/100x100bb.jpg',
                       seller_name='Gameloft',
                       five_star_ratings=2803680,
                       four_star_ratings=243216,
                       three_star_ratings=95109,
                       two_star_ratings=53757,
                       one_star_ratings=94018)
        ]

        _add_model_objects_to_db(apps)

        yield apps

        _delete_model_objects_from_db(apps)


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


def _timestamp_to_datetime(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
