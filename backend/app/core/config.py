from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "Audio Book Converter"
    PORT: int = 8001

settings = Settings()
