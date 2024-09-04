from flask import Blueprint

from compmatrix import blueprints

from compmatrix.api.routes import routes as api_routes
from compmatrix.client.routes import routes as index_routes

client_blueprint: Blueprint = blueprints.create_blueprint('index',
                                                          __name__,
                                                          '/',
                                                          index_routes)
api_blueprint: Blueprint = blueprints.create_blueprint('api',
                                                       __name__,
                                                       '/api',
                                                       api_routes)
