import compmatrix
from compmatrix import db
from compmatrix import models
from compmatrix import routes
from compmatrix import settings


def main():
    app = compmatrix.create_app(settings.Settings())
    with app.app_context():
        sdks = models.SDK.query.all()
        for sdk in sdks:
            print(f'SDK Name: {sdk.name}')
            print(f'Description: {sdk.description}')

    for route in routes.routes:
        print(route.path)


if __name__ == '__main__':
    main()
