from http import HTTPStatus

from flask import Blueprint, Flask

from compmatrix import routing


def test_create_route_obj():
    route_name = 'route_name'
    route_path = '/'
    expected_route_output = 'you have been rick rolled'
    route = routing.Route(route_name,
                          route_path,
                          lambda: expected_route_output)
    assert route.name == route_name
    assert route.path == route_path
    assert route.view_func() == expected_route_output


def test_add_routes_to_blueprint(data_routes):
    name = 'blueprint'
    import_name = 'blueprint_import_name'

    bp = Blueprint(name, import_name)
    routing.add_routes_to_blueprint(bp, data_routes)

    tmp_app = Flask(__name__)
    tmp_app.register_blueprint(bp)

    with tmp_app.test_client() as c:
        for route in data_routes:
            resp = c.get(route.path)
            assert resp.status_code == HTTPStatus.OK
