import argparse

from compmatrix import create_app

import config

app = create_app(config.DB_PATH)


def main():
    args_parser: argparse.ArgumentParser = _create_args_parser()
    args: argparse.Namespace = args_parser.parse_args()

    # Best to run the app dev server in debug mode by default, since it's for
    # development purposes anyway. We'll see if we have a need to turn it off
    # later on.
    app.run(host=args.host, port=args.port, debug=True)


def _create_args_parser() -> argparse.ArgumentParser:
    arg_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='App server for CompMatrix')
    arg_parser.add_argument('--host', type=str,
                            help='Host the app dev server will use',
                            default='127.0.0.1')
    arg_parser.add_argument('-p', '--port', type=int,
                            help='Port the app dev server will use',
                            default=10982)

    return arg_parser


if __name__ == '__main__':
    main()
