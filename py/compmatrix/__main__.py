import compmatrix
from compmatrix import db
from compmatrix import routes
from compmatrix import settings


def main():
    app = compmatrix.create_app(settings.Settings(), routes.routes)
    app.run()


if __name__ == '__main__':
    main()
