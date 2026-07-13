from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent # resolves to the /backend folder
DB_USERS_PATH = PROJECT_ROOT / "database" / "users"