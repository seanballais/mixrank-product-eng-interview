from pathlib import Path

BASE_DIR: Path = Path(__file__).parent.resolve()
DB_PATH: Path = BASE_DIR / 'data.db'
