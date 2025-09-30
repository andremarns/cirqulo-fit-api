import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cirqulofit_user:cirqulofit_password@db:5432/cirqulofit")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # GIPHY API para GIFs de exercícios
    GIPHY_API_KEY: str = os.getenv("GIPHY_API_KEY", "your-giphy-api-key")
    GIPHY_BASE_URL: str = "https://api.giphy.com/v1/gifs"

settings = Settings()
