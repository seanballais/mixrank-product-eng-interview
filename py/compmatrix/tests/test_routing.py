from http import HTTPStatus

from flask import Blueprint, Flask
import pytest

from compmatrix import routing


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


def test_create_route_obj():
    route_path = '/'
    expected_route_output = 'you have been rick rolled'
    route = routing.Route(route_path, lambda: expected_route_output)
    assert route.path == route_path
    assert route.view_func() == expected_route_output


def test_add_routes_to_blueprint(setup_data):
    name = 'blueprint'
    import_name = 'blueprint_import_name'

    bp = Blueprint(name, import_name)
    routing.add_routes_to_blueprint(bp, setup_data['routes'])

    tmp_app = Flask(__name__)
    tmp_app.register_blueprint(bp)

    with tmp_app.test_client() as c:
        for route in setup_data['routes']:
            resp = c.get(route.path)
            assert resp.status_code == HTTPStatus.OK
