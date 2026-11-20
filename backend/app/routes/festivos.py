from datetime import date

import psycopg
from flask import Blueprint, request

from ..database import get_connection


festivos_bp = Blueprint("festivos", __name__)


@festivos_bp.get("")
def listar_festivos():
    raw_year = request.args.get("anio")
    if raw_year is None:
        return {"mensaje": "El parámetro anio es obligatorio"}, 400
    try:
        year = int(raw_year)
    except ValueError:
        return {"mensaje": "El parámetro anio debe ser un año válido"}, 400
    if year < date.min.year or year > date.max.year:
        return {"mensaje": "El parámetro anio está fuera de rango"}, 400

    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, fecha, nombre, anio
                  FROM dias_festivos
                 WHERE anio = %s
                 ORDER BY fecha
                """,
                (year,),
            ).fetchall()
    except psycopg.Error:
        return {
            "mensaje": "No fue posible consultar los días festivos"
        }, 503

    return {
        "anio": year,
        "dias_festivos": [
            {
                **row,
                "fecha": row["fecha"].isoformat(),
            }
            for row in rows
        ],
    }, 200
