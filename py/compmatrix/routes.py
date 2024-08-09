import typing

from compmatrix import controllers


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


BASE_API_ROUTE: typing.Final[str] = '/api'
BASE_V1_API_ROUTE: typing.Final[str] = f'{BASE_API_ROUTE}/v1'


routes = [
    Route(f'{BASE_V1_API_ROUTE}/sdks', controllers.sdks.index)
]
