from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    GEMINI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "lexwarden-safe-clauses"
    MONGO_URI: str = "mongodb://localhost:27017/lexwarden"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
