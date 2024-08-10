import typing

from flask import Blueprint


class Route:
    def __init__(self, path: str, view_func: typing.Callable):
        self._path = path
        self._view_func = view_func

    @property
    def path(self) -> str:
        return self._path

    @property
    def view_func(self) -> typing.Callable:
        return self._view_func


def add_routes_to_blueprint(blueprint: Blueprint, routes: list[Route]):
    for route in routes:
        blueprint.add_url_rule(route.path, view_func=route.view_func)
