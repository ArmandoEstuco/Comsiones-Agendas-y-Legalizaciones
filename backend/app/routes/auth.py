import re

import psycopg
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from flask_limiter.util import get_remote_address

from ..extensions import limiter
from ..services.auth_service import authenticate_user


auth_bp = Blueprint("auth", __name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/login")
@limiter.limit("5 per 15 minutes", key_func=get_remote_address)
def login():
    payload = request.get_json(silent=True) or {}
    correo = payload.get("correo")
    contrasena = payload.get("contrasena")

    if (
        not isinstance(correo, str)
        or not EMAIL_PATTERN.fullmatch(correo.strip())
        or not isinstance(contrasena, str)
        or not contrasena
    ):
        return {"mensaje": "Credenciales inválidas"}, 401

    try:
        user = authenticate_user(correo.strip(), contrasena)
    except (psycopg.Error, ValueError):
        return {"mensaje": "El servicio no está disponible en este momento"}, 503

    if user is None:
        return {"mensaje": "Credenciales inválidas"}, 401

    token = create_access_token(
        identity=user["id"],
        additional_claims={"rol": user["rol"]},
    )
    return {
        "mensaje": "Inicio de sesión exitoso",
        "token": token,
        "usuario": user,
    }, 200
