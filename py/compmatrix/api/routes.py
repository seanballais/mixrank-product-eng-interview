import typing

from compmatrix.routing import Route

from compmatrix.api import views

API_VERSION_STRING_V1: typing.Final[str] = 'v1'

routes: list[Route] = [
    Route('sdks_v1', f'/{API_VERSION_STRING_V1}/sdks', views.sdks.index),
    Route('sdk_compmatrix_numbers_v1',
          f'/{API_VERSION_STRING_V1}/sdk-compmatrix/numbers',
          views.sdk_compmatrix.numbers.index),
    Route('sdk_compmatrix_apps_v1',
          f'/{API_VERSION_STRING_V1}/sdk-compmatrix/apps',
          views.sdk_compmatrix.apps.index)
]
