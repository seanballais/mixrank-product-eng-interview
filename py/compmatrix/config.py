# Based off of: https://github.com/miguelgrinberg/microblog/blob/main/config.py
from pathlib import Path


class Config:
    BASE_DIR: Path = Path(__file__).parent.parent.parent.resolve()
    DB_DIR: Path = BASE_DIR / 'data.db'
    HOST: str = '127.0.0.1'
    PORT: int = 5000
    DEBUG: bool = True
