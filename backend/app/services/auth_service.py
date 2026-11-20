import bcrypt
import psycopg

from ..database import get_connection


def authenticate_user(correo: str, contrasena: str) -> dict | None:
    query = """
        SELECT u.documento_usuario, u.correo, u.contrasena_hash, u.estado,
               r.nombre_rol
          FROM usuarios AS u
          JOIN roles AS r ON r.id_rol = u.id_rol
         WHERE LOWER(u.correo) = LOWER(%s)
         LIMIT 1
    """
    with get_connection() as connection:
        user = connection.execute(query, (correo,)).fetchone()

    if not user or user["estado"].lower() != "activo":
        return None

    stored_hash = user["contrasena_hash"].encode("utf-8")
    if stored_hash.startswith(b"$2y$"):
        stored_hash = b"$2b$" + stored_hash[4:]
    if not bcrypt.checkpw(contrasena.encode("utf-8"), stored_hash):
        return None

    return {
        "id": user["documento_usuario"],
        "correo": user["correo"],
        "rol": user["nombre_rol"],
    }


def database_is_reachable() -> bool:
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
        return True
    except psycopg.Error:
        return False
