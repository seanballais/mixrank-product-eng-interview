from compmatrix.client import views
from compmatrix.routing import Route

routes: list[Route] = [
    Route('index', '/', views.index)
]
