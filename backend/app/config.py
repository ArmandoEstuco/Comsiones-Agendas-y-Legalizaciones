import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()


def parse_expiration(value: str) -> timedelta | int:
    if value.isdigit():
        return int(value)
    if value.endswith("h") and value[:-1].isdigit():
        return timedelta(hours=int(value[:-1]))
    if value.endswith("m") and value[:-1].isdigit():
        return timedelta(minutes=int(value[:-1]))
    if value.endswith("d") and value[:-1].isdigit():
        return timedelta(days=int(value[:-1]))
    raise RuntimeError(
        "JWT_ACCESS_TOKEN_EXPIRES debe ser segundos o una duración como 8h"
    )


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "local-development-only")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ACCESS_TOKEN_EXPIRES = parse_expiration(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "8h")
    )
    MAX_SIGNATURE_SIZE = 1_048_576
    MAX_CONTENT_LENGTH = MAX_SIGNATURE_SIZE
    FIRMAS_UPLOAD_FOLDER = os.getenv(
        "FIRMAS_UPLOAD_FOLDER",
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "private",
            "firmas",
        ),
    )

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5438"))
    DB_NAME = os.getenv("DB_NAME", "comisiones")
    DB_USER = os.getenv("DB_USER", "admin_comisiones")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    @classmethod
    def validate(cls):
        if len(cls.JWT_SECRET_KEY) < 32:
            raise RuntimeError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
