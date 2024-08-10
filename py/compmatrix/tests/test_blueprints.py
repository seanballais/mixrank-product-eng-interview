from http import HTTPStatus

from flask import Flask
import pytest

from compmatrix import blueprints, routing


@pytest.fixture
def setup_data():
    def test_view_index():
        return ''

    def test_view_a():
        return 'a'

    def test_view_ab():
        return 'ab'

    routes = [
        routing.Route('/', test_view_index),
        routing.Route('/a', test_view_a),
        routing.Route('/a/b', test_view_ab),
    ]
    yield {
        'routes': routes
    }


def test_create_blueprint(setup_data):
    name = 'app_module'
    import_name = 'app_module_import_name'

    bp = blueprints.create_blueprint(name, import_name, '/',
                                     setup_data['routes'])
    tmp_app = Flask(__name__)
    tmp_app.register_blueprint(bp)

    with tmp_app.test_client() as c:
        for route in setup_data['routes']:
            resp = c.get(route.path)
            assert resp.status_code == HTTPStatus.OK
