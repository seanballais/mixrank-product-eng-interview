from compmatrix.app_modules import AppModule

from compmatrix.api.routes import routes

api_module: AppModule = AppModule('api', __name__, '/api', routes)
