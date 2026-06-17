import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    #Database Config
    PROJECT_NAME:str = "FastAPI Testing"
    PROJECT_VERSION: str = "1.0.0"
    POSTGRES_USER : str = os.getenv("DB_USER")
    POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
    POSTGRES_SERVER : str = os.getenv("DB_SERVER","localhost")
    POSTGRES_PORT : str = os.getenv("DB_PORT",5432)
    POSTGRES_DB : str = os.getenv("DB_NAME","tdd")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    #APP URL
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8000")

    #JWT Config
    SECRET_KEY              : str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM               : str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "30"))

    #OTP Config
    SMTP_HOST          : str = os.getenv("SMTP_HOST")
    SMTP_PORT          : str = os.getenv("SMTP_PORT")
    SMTP_USERNAME      : str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD      : str = os.getenv("SMTP_PASSWORD")
    SMTP_FROM          : str = os.getenv("SMTP_FROM")
    OTP_EXPIRE_MINUTES : int = int(os.getenv("OTP_EXPIRE_MINUTES"))

configs = Config()