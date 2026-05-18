import os
from dotenv import load_dotenv

load_dotenv(".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # evitar que toda vez que houver uma modificação ficar checando
