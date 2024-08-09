# Some ideas taken from: https://github.com/miguelgrinberg/microblog/blob/main/app/__init__.py
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from compmatrix import routes


def create_application(db: SQLAlchemy, db_path: Path,
                       routes: list[routes.Route]) -> Flask:
    db_uri: str = f'sqlite:///{db_path}'

    app: Flask = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    _load_routes(app, routes)

    db.init_app(app)

    return app


def _load_routes(application: Flask, routes: list[routes.Route]):
    for route in routes:
        application.add_url_rule(route.path, view_func=route.view_func)
