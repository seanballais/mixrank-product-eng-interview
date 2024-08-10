from flask import Blueprint

from compmatrix import routing


class AppModule:
    def __init__(self, name: str, import_name, url_prefix: str,
                 routes: list[routing.Route],
                 **kwargs):
        self._bp = Blueprint(name, import_name, **kwargs)
        routing.add_routes_to_blueprint(self._bp, routes)

        self._url_prefix = url_prefix
        if self._url_prefix[0] != '/':
            self._url_prefix = '/' + self._url_prefix

    @property
    def blueprint(self) -> Blueprint:
        return self._bp

    @property
    def url_prefix(self) -> str:
        return self._url_prefix
