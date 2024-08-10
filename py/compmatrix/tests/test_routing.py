from http import HTTPStatus

from flask import Blueprint, Flask

from compmatrix import routing

from compmatrix.tests.fixtures import test_data_routes


def test_create_route_obj():
    route_path = '/'
    expected_route_output = 'you have been rick rolled'
    route = routing.Route(route_path, lambda: expected_route_output)
    assert route.path == route_path
    assert route.view_func() == expected_route_output


def test_add_routes_to_blueprint(test_data_routes):
    name = 'blueprint'
    import_name = 'blueprint_import_name'

    bp = Blueprint(name, import_name)
    routing.add_routes_to_blueprint(bp, test_data_routes)

    tmp_app = Flask(__name__)
    tmp_app.register_blueprint(bp)

    with tmp_app.test_client() as c:
        for route in test_data_routes:
            resp = c.get(route.path)
            assert resp.status_code == HTTPStatus.OK
