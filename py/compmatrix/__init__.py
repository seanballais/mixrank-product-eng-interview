# Basing from https://hackersandslackers.com/flask-blueprints/
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(db_path: Path) -> Flask:
    db_uri: str = f'sqlite:///{db_path}'

    app: Flask = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    #    app.config['SQLALCHEMY_ECHO'] = True

    db.init_app(app)

    with app.app_context():
        # This part can still be improved.
        from compmatrix.api.module import api_blueprint

        app.register_blueprint(api_blueprint)

    return app
