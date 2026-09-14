import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Settings():

    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_URL: str = os.getenv("DATABASE_URL")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    @property
    def DATABASE_URL(self) -> str:
        return self.DB_URL

settings = Settings()

# Validate Supabase credentials right after instantiating settings
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

# Create the global Supabase client instance directly in this file
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

