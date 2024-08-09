from py.compmatrix import application, db, routes

import config

app = application.create_application(db, config.DB_PATH, routes.routes)


def main():
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == '__main__':
    main()
