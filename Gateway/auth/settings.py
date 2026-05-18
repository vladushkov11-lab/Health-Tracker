from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEYS= os.getenv("SECRET_KEYS")
ALGORITHMS = os.getenv("ALGORITHMS")
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    SECRET_KEY: str = SECRET_KEYS
    ALGORITHM: str = ALGORITHMS
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()