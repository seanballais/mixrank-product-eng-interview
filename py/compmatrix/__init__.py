# Some ideas taken from: https://github.com/miguelgrinberg/microblog/blob/main/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from compmatrix import routes, settings


db: SQLAlchemy = SQLAlchemy()


def create_app(settings_class: settings.Settings, routes: list[routes.Route]) -> Flask:
    db_uri: str = f'sqlite:///{settings_class.DB_DIR}'

    app: Flask = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    _load_routes(app, routes)

    db.init_app(app)

    return app


def _load_routes(app: Flask, routes: list[routes.Route]):
    for route in routes:
        app.add_url_rule(route.path, view_func=route.view_func)
