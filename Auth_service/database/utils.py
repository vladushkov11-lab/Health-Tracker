from dotenv import load_dotenv
import secrets
import os
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_HOST_ALEMBIC = os.getenv("DB_HOST_ALEMBIC")
DB_PORT_ALEMBIC = os.getenv("DB_PORT_ALEMBIC")

def get_db_url():
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_db_alembic():
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST_ALEMBIC}:{DB_PORT_ALEMBIC}/{DB_NAME}"

def generate_id_user(length: int = 20) -> str:
    return secrets.token_urlsafe(length)