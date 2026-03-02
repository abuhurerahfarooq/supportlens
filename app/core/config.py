import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///supportlens.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_HEALTH_TIMEOUT_SECONDS = float(os.getenv("LLM_HEALTH_TIMEOUT_SECONDS", "3"))
    LLM_HEALTH_CACHE_TTL_SECONDS = float(os.getenv("LLM_HEALTH_CACHE_TTL_SECONDS", "30"))
