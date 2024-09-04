# Basing from https://hackersandslackers.com/flask-blueprints/
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(db_path: Path,
               assets_folder_path: Path | None = None,
               template_folder_path: Path | None = None) -> Flask:
    db_uri: str = f'sqlite:///{db_path}'

    app: Flask = Flask(__name__,
                       static_folder=assets_folder_path,
                       template_folder=template_folder_path,
                       static_url_path='/assets')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    db.init_app(app)

    with app.app_context():
        # This part can still be improved.
        from compmatrix.api import module

        app.register_blueprint(module.client_blueprint)
        app.register_blueprint(module.api_blueprint)

    return app
