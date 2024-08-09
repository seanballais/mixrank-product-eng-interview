from pathlib import Path


DEBUG: bool = True

BASE_DIR: Path = Path(__file__).parent.resolve()
DB_PATH: Path = BASE_DIR / 'data.db'
HOST: str = '127.0.0.1'
PORT: int = 10982  # Break it up to 109 and 82. 109 -> 'M'. 82 -> 'R'.
