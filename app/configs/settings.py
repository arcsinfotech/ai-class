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

    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = "HS256"

    DB_URL: str = ''

    API_PREFIX: str = ''
    PORT: int = 9000

settings = ApplicationSettings()
