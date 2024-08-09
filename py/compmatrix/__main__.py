from compmatrix import app, app_config


def main():
    app.run(host=app_config.HOST,
            port=app_config.PORT, debug=app_config.DEBUG)


if __name__ == '__main__':
    main()
