import typing

from compmatrix.routing import Route

from compmatrix.api import views

API_VERSION_STRING: typing.Final[str] = 'v1'

routes = [
    Route(f'/{API_VERSION_STRING}/sdks', views.sdks.index),
    Route(f'/{API_VERSION_STRING}/sdk-compmatrix/numbers',
          views.sdk_compmatrix.numbers.index)
]
