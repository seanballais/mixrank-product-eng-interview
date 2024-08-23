import os
from pathlib import Path

import pytest

from compmatrix import create_app, db, routing


@pytest.fixture(scope='session')
def app():
    test_db_path = Path(__file__).parent.resolve() / 'test.db'
    app = create_app(test_db_path)
    with app.app_context():
        db.create_all()

    yield app

    # Clean up.
    if test_db_path.exists():
        os.remove(test_db_path)


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def data_routes():
    def test_view_index():
        return ''

    def test_view_a():
        return 'a'

    def test_view_ab():
        return 'ab'

    routes = [
        routing.Route('index', '/', test_view_index),
        routing.Route('a', '/a', test_view_a),
        routing.Route('ab', '/a/b', test_view_ab),
    ]
    yield routes
