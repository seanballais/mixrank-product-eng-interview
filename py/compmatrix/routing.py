import typing

from flask import Blueprint


class Route:
    def __init__(self, name: str, path: str, view_func: typing.Callable):
        self._name = name
        self._path = path
        self._view_func = view_func

    @property
    def name(self):
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def view_func(self) -> typing.Callable:
        return self._view_func


def add_routes_to_blueprint(blueprint: Blueprint, routes: list[Route]):
    for route in routes:
        blueprint.add_url_rule(route.path,
                               endpoint=route.name,
                               view_func=route.view_func)
