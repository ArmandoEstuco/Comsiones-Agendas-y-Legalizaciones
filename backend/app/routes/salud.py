import psycopg
from flask import Blueprint

from ..database import get_connection


salud_bp = Blueprint("salud", __name__)


@salud_bp.get("")
def salud():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
    except psycopg.Error:
        return {
            "estado": "error",
            "base_datos": "no disponible",
            "mensaje": "La base de datos no está disponible",
        }, 503

    return {"estado": "ok", "base_datos": "conectada"}, 200
