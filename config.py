from pathlib import Path

BASE_DIR: Path = Path(__file__).parent.resolve()
DB_PATH: Path = BASE_DIR / 'data.db'

ASSETS_PATH: Path = BASE_DIR / 'py/compmatrix/client/assets'
TEMPLATES_PATH: Path = BASE_DIR / 'py/compmatrix/client/templates'
