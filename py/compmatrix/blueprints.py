from flask import Blueprint

from compmatrix import routing


def create_blueprint(name: str, import_name: str, url_prefix: str,
                     routes: list[routing.Route], **kwargs) -> Blueprint:
    bp: Blueprint = Blueprint(name, import_name, url_prefix=url_prefix,
                              **kwargs)
    routing.add_routes_to_blueprint(bp, routes)

    return bp
