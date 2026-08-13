import logging

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

log = logging.getLogger(__name__)

# Set up logging to show environment loading
logging.basicConfig(level=logging.WARNING)

if not load_dotenv():
    log.error(f"Environment file .env not found.")
else:
    log.info(f"Successfully loaded environment from .env")

class ApplicationSettings(BaseSettings):
    """Define application configuration model.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.
    """

    model_config = ConfigDict(case_sensitive=True)

    DEBUG: bool = False
    PROJECT_NAME: str = "AI Class"
    DOCS_URL: str = "/"
    OPENAPI_URL: str = "/openapi.json"
    REDOC_URL: str = "/redoc"
    
    OPENAI_API_KEY: str = ''

    ENV: str = 'development'

    SECRET_KEY: str = 'super-secret-key'
    ALGO: str = 'HS256'
    ACCESS_TOKEN_EXP: int = 30
    REFRES_TOKEN_EXP: int = 7

    DB_URL: str = ''
    REDIS_URI: str = ''

    GITHUB_CLIENT_ID: str = ''
    GITHUB_CLIENT_SECRET: str = ''
    GITHUB_REDIRECT_URI: str =  'http://localhost:9000/auth/github/callback'

    API_PREFIX: str = ''
    PORT: int = 9000
    FRONTEND_URL: str = 'http://localhost:5173'

settings = ApplicationSettings()
