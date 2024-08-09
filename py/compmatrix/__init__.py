# Some ideas taken from: https://github.com/miguelgrinberg/microblog/blob/main/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from compmatrix import routes
from py.compmatrix import config


def create_app(db: SQLAlchemy, config: config.Config,
               routes: list[routes.Route]) -> Flask:
    db_uri: str = f'sqlite:///{config.DB_DIR}'

    app: Flask = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    _load_routes(app, routes)

    db.init_app(app)

    return app


def _load_routes(app: Flask, routes: list[routes.Route]):
    for route in routes:
        app.add_url_rule(route.path, view_func=route.view_func)


# Default app and db objects. We can use this as-is, but we can also use
# create_app() to use a differently configured objects to avoid coupling. We
# should avoid coupling variables as much as we can. Otherwise, we'll be
# slapped by a nasty reality later on. This is not the right time and place
# to be clingy.
db: SQLAlchemy = SQLAlchemy()
app_config: config.Config = config.Config()
app = create_app(db, app_config, routes.routes)
