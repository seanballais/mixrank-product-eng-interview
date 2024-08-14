from datetime import datetime

import pytest

from compmatrix import db
from compmatrix.api import models


@pytest.fixture(scope='session')
def test_db_data(app):
    # We have to put the test database data in one fixture, since the database
    # would get locked if we don't.
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
                       one_star_ratings=94018),
            models.App(name='Bike Race: Free Style Games',
                       company_url='https://www.topfreegames.com/games/'
                                   'bikerace',
                       release_date=None,
                       genre_id=6014,
                       artwork_large_url='https://is1-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/89/db/41/'
                                         '89db41ff-34f2-de25-131e-'
                                         '96abc6057fc4/source/100x100bb.jpg',
                       seller_name='Top Free Games',
                       five_star_ratings=1663004,
                       four_star_ratings=125180,
                       three_star_ratings=54040,
                       two_star_ratings=26050,
                       one_star_ratings=38794),
            models.App(name='Pandora: Music & Podcasts',
                       company_url='http://www.pandora.com/',
                       release_date=_timestamp_to_datetime(
                           '2008-07-11 00:00:00'),
                       genre_id=6011,
                       artwork_large_url='https://is3-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/a5/e8/63/'
                                         'a5e86344-adfe-28c9-2e60-'
                                         '56a18300ad86/source/100x100bb.jpg',
                       seller_name='Pandora Media, Inc.',
                       five_star_ratings=5933106,
                       four_star_ratings=762539,
                       three_star_ratings=261281,
                       two_star_ratings=97646,
                       one_star_ratings=231957),
            models.App(name='Trivia Crack',
                       company_url='http://www.etermax.com',
                       release_date=_timestamp_to_datetime(
                           '2013-10-16 23:50:26'),
                       genre_id=6014,
                       artwork_large_url='https://is5-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/a9/34/1c/'
                                         'a9341cdf-3771-7df7-e0b4-'
                                         '8f2f38794a86/source/100x100bb.jpg',
                       seller_name='Etermax',
                       five_star_ratings=961220,
                       four_star_ratings=271151,
                       three_star_ratings=91572,
                       two_star_ratings=27868,
                       one_star_ratings=58754),
            models.App(name='Solitaire',
                       company_url='https://www.mobilityware.com',
                       release_date=_timestamp_to_datetime(
                           '2010-03-18 00:00:00'),
                       genre_id=6014,
                       artwork_large_url='https://is4-ssl.mzstatic.com/image/'
                                         'thumb/Purple113/v4/7d/a6/fa/'
                                         '7da6faed-435c-9917-0396-'
                                         'ea0813267f2c/source/100x100bb.jpg',
                       seller_name='Mobilityware',
                       five_star_ratings=1953492,
                       four_star_ratings=523566,
                       three_star_ratings=202937,
                       two_star_ratings=76844,
                       one_star_ratings=93069),
            models.App(name='Pinterest',
                       company_url='http://www.pinterest.com',
                       release_date=_timestamp_to_datetime(
                           '2011-04-28 00:00:00'),
                       genre_id=6012,
                       artwork_large_url='https://is5-ssl.mzstatic.com/image/'
                                         'thumb/Purple123/v4/dd/1c/02/'
                                         'dd1c026d-dfba-c796-c511-'
                                         'f9bb917a7f0f/source/100x100bb.jpg',
                       seller_name='Pinterest, Inc.',
                       five_star_ratings=9931250,
                       four_star_ratings=1414778,
                       three_star_ratings=363227,
                       two_star_ratings=95981,
                       one_star_ratings=145133)
        ]
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

        # Expected Competitive Matrix Values
        #
        #            | PayPal | card.io | Chartboost |
        # -----------+--------+---------+------------|
        # PayPal     |      4 |       3 |          3 |
        # card.io    |      2 |       5 |          3 |
        # Chartboost |      3 |       3 |          4 |
        #
        #            | PayPal | (none) |
        # -----------+--------+--------|
        # PayPal     |      4 |      6 |
        # card.io    |      2 |      8 |
        # Chartboost |      3 |      7 |
        #
        #            | PayPal | (none) |
        # -----------+--------+--------|
        # card.io    |      2 |      8 |
        # (none)     |      4 |      8 |
        #
        # Interpretations:
        #   App 0  - from SDK 1 and 2 to SDK 0
        #   App 1  - from SDK 0 and 2 to SDK 1
        #   App 2  - from SDK 0 and 1 to SDK 2
        #   App 3  - from SDK 1 and 2 to SDK 0
        #   App 4  - from SDK 0 and 2 to SDK 1
        #   App 5  - from SDK 0 and 1 to SDK 2
        #   App 6  - from SDK 0 to SDK 1
        #   App 7  - from SDK 0 to SDK 2
        #   App 8  - from SDK 1 to SDK 2
        #   App 9  - using SDK 1
        #   App 10 - used to use SDK 1, but we no longer have further SDK info
        #   App 11 - used to use SDK 1, but we no longer have further SDK info
        #   App 12 - from SDK 2 to SDK 0 and 1
        #   App 13 - using SDK 1
        #   App 14 - no info on SDKs used
        app_sdks = [
            models.AppSDK(app=apps[0], sdk=sdks[0], installed=True),
            models.AppSDK(app=apps[0], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[0], sdk=sdks[2], installed=False),
            models.AppSDK(app=apps[1], sdk=sdks[0], installed=False),
            models.AppSDK(app=apps[1], sdk=sdks[1], installed=True),
            models.AppSDK(app=apps[1], sdk=sdks[2], installed=False),
            models.AppSDK(app=apps[2], sdk=sdks[0], installed=False),
            models.AppSDK(app=apps[2], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[2], sdk=sdks[2], installed=True),
            models.AppSDK(app=apps[3], sdk=sdks[0], installed=True),
            models.AppSDK(app=apps[3], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[3], sdk=sdks[2], installed=False),
            models.AppSDK(app=apps[4], sdk=sdks[0], installed=False),
            models.AppSDK(app=apps[4], sdk=sdks[1], installed=True),
            models.AppSDK(app=apps[4], sdk=sdks[2], installed=False),
            models.AppSDK(app=apps[5], sdk=sdks[0], installed=False),
            models.AppSDK(app=apps[5], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[5], sdk=sdks[2], installed=True),
            models.AppSDK(app=apps[6], sdk=sdks[0], installed=False),
            models.AppSDK(app=apps[6], sdk=sdks[1], installed=True),
            models.AppSDK(app=apps[7], sdk=sdks[0], installed=False),
            models.AppSDK(app=apps[7], sdk=sdks[2], installed=True),
            models.AppSDK(app=apps[8], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[8], sdk=sdks[2], installed=True),
            models.AppSDK(app=apps[9], sdk=sdks[0], installed=True),
            models.AppSDK(app=apps[10], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[11], sdk=sdks[1], installed=False),
            models.AppSDK(app=apps[12], sdk=sdks[0], installed=True),
            models.AppSDK(app=apps[12], sdk=sdks[1], installed=True),
            models.AppSDK(app=apps[12], sdk=sdks[2], installed=False),
            models.AppSDK(app=apps[13], sdk=sdks[1], installed=True)
        ]

        _add_model_objects_to_db(apps)
        _add_model_objects_to_db(sdks)
        _add_model_objects_to_db(app_sdks)

        yield {
            'apps': apps,
            'sdks': sdks,
            'app_sdks': app_sdks
        }

        _delete_model_objects_from_db(app_sdks)
        _delete_model_objects_from_db(sdks)
        _delete_model_objects_from_db(apps)


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
