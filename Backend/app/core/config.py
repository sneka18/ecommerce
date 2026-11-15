import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env file from the Backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "AI-Enhanced E-Commerce Platform")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "ai_ecommerce_db")

    @property
    def DATABASE_URL(self) -> str:
        encoded_pwd = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        return f"mysql+pymysql://{self.DB_USER}:{encoded_pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # JWT Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_ai_ecommerce_platform_academic_project_2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Directories
    ROOT_DIR: Path = BASE_DIR.parent
    BACKEND_DIR: Path = BASE_DIR
    FRONTEND_DIR: Path = BASE_DIR.parent / "Frontend"
    ML_DIR: Path = BASE_DIR.parent / "ML"
    ML_MODELS_DIR: Path = ML_DIR / "models"
    ML_DATASET_DIR: Path = ML_DIR / "dataset"


settings = Settings()

