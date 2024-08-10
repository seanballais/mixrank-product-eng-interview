# Some ideas taken from: https://github.com/miguelgrinberg/microblog/blob/main/app/__init__.py
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db: SQLAlchemy = SQLAlchemy()


def create_app(db_path: Path) -> Flask:
    db_uri: str = f'sqlite:///{db_path}'

    app: Flask = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    db.init_app(app)

    return app
