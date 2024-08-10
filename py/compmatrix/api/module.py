from flask import Blueprint

from compmatrix import blueprints

from compmatrix.api.routes import routes

api_blueprint: Blueprint = blueprints.create_blueprint('api', __name__, '/api',
                                                       routes)
