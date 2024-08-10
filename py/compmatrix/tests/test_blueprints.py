from http import HTTPStatus

from flask import Flask

from compmatrix import blueprints

from compmatrix.tests.fixtures import test_data_routes


def test_create_blueprint(test_data_routes):
    name = 'blueprints'
    import_name = 'blueprints_import_name'

    bp = blueprints.create_blueprint(name, import_name, '/', test_data_routes)
    tmp_app = Flask(__name__)
    tmp_app.register_blueprint(bp)

    with tmp_app.test_client() as c:
        for route in test_data_routes:
            resp = c.get(route.path)
            assert resp.status_code == HTTPStatus.OK
