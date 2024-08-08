# Based off of: https://github.com/miguelgrinberg/microblog/blob/main/config.py
from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).parent.parent.parent.resolve()
    DB_DIR: Path = BASE_DIR / 'data.db'
