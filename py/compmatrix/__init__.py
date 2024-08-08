# Some ideas taken from: https://github.com/miguelgrinberg/microblog/blob/main/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from compmatrix import settings


db: SQLAlchemy = SQLAlchemy()


def create_app(settings_class: settings.Settings):
    db_uri: str = f'sqlite:///{settings_class.DB_DIR}'

    app: Flask = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    db.init_app(app)

    return app
