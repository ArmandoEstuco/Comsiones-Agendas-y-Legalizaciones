import re
from datetime import date

import psycopg
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from ..database import get_connection
from ..utils.permisos import COMISIONADO_CONTRATISTA, requiere_roles


perfil_bp = Blueprint("perfil", __name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PROFILE_FIELDS = {"nombres", "apellidos", "correo"}
CONTRACT_FIELDS = {
    "numero_contrato",
    "anio",
    "fecha_inicio",
    "fecha_fin",
    "objeto_contractual",
}


def reject_unknown_fields(payload, allowed):
    unknown = set(payload) - allowed
    if unknown:
        return {
            "mensaje": "Campos no permitidos",
            "campos": sorted(unknown),
        }, 400
    return None


def valid_text(value, field, max_length, allow_empty=False):
    if not isinstance(value, str):
        return f"El campo {field} debe ser texto"
    value = value.strip()
    if not allow_empty and not value:
        return f"El campo {field} no puede estar vacío"
    if len(value) > max_length:
        return f"El campo {field} supera la longitud máxima"
    return None


def parse_date(value, field):
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, f"El campo {field} debe tener formato YYYY-MM-DD"
    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, f"El campo {field} debe tener formato YYYY-MM-DD"


@perfil_bp.get("")
@requiere_roles(COMISIONADO_CONTRATISTA)
def obtener_perfil():
    documento = get_jwt_identity()
    try:
        with get_connection() as connection:
            usuario = connection.execute(
                """
                SELECT u.documento_usuario, u.tipo_documento,
                       u.nombres, u.apellidos, u.correo, u.estado,
                       r.nombre_rol
                  FROM usuarios AS u
                  JOIN roles AS r ON r.id_rol = u.id_rol
                 WHERE u.documento_usuario = %s
                   AND r.nombre_rol = %s
                """,
                (documento, COMISIONADO_CONTRATISTA),
            ).fetchone()
    except psycopg.Error:
        return {"mensaje": "No fue posible consultar el perfil"}, 503

    if usuario is None:
        return {"mensaje": "Perfil no encontrado"}, 404

    return {"perfil": usuario}, 200


@perfil_bp.patch("")
@requiere_roles(COMISIONADO_CONTRATISTA)
def actualizar_perfil():
    documento = get_jwt_identity()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {"mensaje": "Debe enviar un objeto JSON"}, 400

    error = reject_unknown_fields(payload, PROFILE_FIELDS)
    if error:
        return error
    if not payload:
        return {"mensaje": "Debe enviar al menos un campo permitido"}, 400

    updates = {}
    if "nombres" in payload:
        error_message = valid_text(payload["nombres"], "nombres", 100)
        if error_message:
            return {"mensaje": error_message}, 400
        updates["nombres"] = payload["nombres"].strip()
    if "apellidos" in payload:
        error_message = valid_text(payload["apellidos"], "apellidos", 100)
        if error_message:
            return {"mensaje": error_message}, 400
        updates["apellidos"] = payload["apellidos"].strip()
    if "correo" in payload:
        correo = payload["correo"]
        if not isinstance(correo, str):
            return {"mensaje": "El correo debe ser texto"}, 400
        correo = correo.strip()
        if (
            len(correo) > 150
            or not EMAIL_PATTERN.fullmatch(correo)
        ):
            return {"mensaje": "El correo no tiene un formato válido"}, 400
        updates["correo"] = correo

    set_clause = ", ".join(f"{field} = %s" for field in updates)
    values = list(updates.values())
    values.append(documento)

    try:
        with get_connection() as connection:
            try:
                result = connection.execute(
                    f"""
                    UPDATE usuarios AS u
                       SET {set_clause}
                     WHERE u.documento_usuario = %s
                       AND u.id_rol = (
                           SELECT id_rol FROM roles
                            WHERE nombre_rol = %s
                       )
                    """,
                    (*values, COMISIONADO_CONTRATISTA),
                )
                if result.rowcount == 0:
                    connection.rollback()
                    return {"mensaje": "Perfil no encontrado"}, 404
                connection.commit()
            except psycopg.errors.UniqueViolation:
                connection.rollback()
                return {"mensaje": "El correo ya está registrado"}, 409
            except psycopg.Error:
                connection.rollback()
                raise
    except psycopg.Error:
        return {"mensaje": "No fue posible actualizar el perfil"}, 503

    return {"mensaje": "Perfil actualizado correctamente"}, 200


@perfil_bp.get("/contratos")
@requiere_roles(COMISIONADO_CONTRATISTA)
def listar_contratos():
    documento = get_jwt_identity()
    try:
        with get_connection() as connection:
            contratos = connection.execute(
                """
                SELECT id_contrato, numero_contrato, anio,
                       fecha_inicio, fecha_fin, objeto_contractual
                  FROM contratos
                 WHERE documento_contratista = %s
                 ORDER BY anio DESC, id_contrato DESC
                """,
                (documento,),
            ).fetchall()
    except psycopg.Error:
        return {"mensaje": "No fue posible consultar los contratos"}, 503

    return {"contratos": [dict(row) for row in contratos]}, 200


def consultar_contrato_propiedad(connection, documento, id_contrato):
    return connection.execute(
        """
        SELECT id_contrato, numero_contrato, anio,
               fecha_inicio, fecha_fin, objeto_contractual
          FROM contratos
         WHERE id_contrato = %s
           AND documento_contratista = %s
        """,
        (id_contrato, documento),
    ).fetchone()


@perfil_bp.get("/contratos/<int:id_contrato>")
@requiere_roles(COMISIONADO_CONTRATISTA)
def obtener_contrato(id_contrato):
    documento = get_jwt_identity()
    try:
        with get_connection() as connection:
            contrato = consultar_contrato_propiedad(
                connection, documento, id_contrato
            )
    except psycopg.Error:
        return {"mensaje": "No fue posible consultar el contrato"}, 503

    if contrato is None:
        return {"mensaje": "Contrato no encontrado"}, 404
    return {"contrato": contrato}, 200


@perfil_bp.patch("/contratos/<int:id_contrato>")
@requiere_roles(COMISIONADO_CONTRATISTA)
def actualizar_contrato(id_contrato):
    documento = get_jwt_identity()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {"mensaje": "Debe enviar un objeto JSON"}, 400

    error = reject_unknown_fields(payload, CONTRACT_FIELDS)
    if error:
        return error
    if not payload:
        return {"mensaje": "Debe enviar al menos un campo permitido"}, 400

    updates = {}
    if "numero_contrato" in payload:
        error_message = valid_text(
            payload["numero_contrato"], "numero_contrato", 50
        )
        if error_message:
            return {"mensaje": error_message}, 400
        updates["numero_contrato"] = payload["numero_contrato"].strip()
    if "anio" in payload:
        anio = payload["anio"]
        if isinstance(anio, bool) or not isinstance(anio, int):
            return {"mensaje": "El campo anio debe ser un entero"}, 400
        if anio < 1900 or anio > 2100:
            return {"mensaje": "El campo anio está fuera de rango"}, 400
        updates["anio"] = anio
    if "fecha_inicio" in payload:
        parsed, error_message = parse_date(
            payload["fecha_inicio"], "fecha_inicio"
        )
        if error_message:
            return {"mensaje": error_message}, 400
        updates["fecha_inicio"] = parsed
    if "fecha_fin" in payload:
        parsed, error_message = parse_date(payload["fecha_fin"], "fecha_fin")
        if error_message:
            return {"mensaje": error_message}, 400
        updates["fecha_fin"] = parsed
    if "fecha_inicio" in updates and "fecha_fin" in updates:
        if (
            updates["fecha_inicio"] is not None
            and updates["fecha_fin"] is not None
            and updates["fecha_fin"] < updates["fecha_inicio"]
        ):
            return {
                "mensaje": "fecha_fin no puede ser anterior a fecha_inicio"
            }, 400
    if "objeto_contractual" in payload:
        objeto = payload["objeto_contractual"]
        if objeto is not None:
            error_message = valid_text(
                objeto, "objeto_contractual", 100000, allow_empty=True
            )
            if error_message:
                return {"mensaje": error_message}, 400
            objeto = objeto.strip() or None
        updates["objeto_contractual"] = objeto

    set_clause = ", ".join(f"{field} = %s" for field in updates)
    values = list(updates.values())

    try:
        with get_connection() as connection:
            contrato = consultar_contrato_propiedad(
                connection, documento, id_contrato
            )
            if contrato is None:
                return {"mensaje": "Contrato no encontrado"}, 404

            if "fecha_inicio" not in updates or "fecha_fin" not in updates:
                if (
                    "fecha_inicio" not in updates
                    and "fecha_fin" not in updates
                ):
                    pass
                else:
                    fecha_inicio = updates.get(
                        "fecha_inicio", contrato["fecha_inicio"]
                    )
                    fecha_fin = updates.get("fecha_fin", contrato["fecha_fin"])
                    if (
                        fecha_inicio is not None
                        and fecha_fin is not None
                        and fecha_fin < fecha_inicio
                    ):
                        return {
                            "mensaje": (
                                "fecha_fin no puede ser anterior a fecha_inicio"
                            )
                        }, 400

            try:
                connection.execute(
                    f"""
                    UPDATE contratos
                       SET {set_clause}
                     WHERE id_contrato = %s
                       AND documento_contratista = %s
                    """,
                    (*values, id_contrato, documento),
                )
                connection.commit()
            except psycopg.errors.UniqueViolation:
                connection.rollback()
                return {
                    "mensaje": "Ya existe un contrato con ese número y año"
                }, 409
            except psycopg.Error:
                connection.rollback()
                raise
    except psycopg.Error:
        return {"mensaje": "No fue posible actualizar el contrato"}, 503

    return {"mensaje": "Contrato actualizado correctamente"}, 200


def obtener_contrato_para_operacion(connection, documento, id_contrato):
    return consultar_contrato_propiedad(
        connection, documento, id_contrato
    )


@perfil_bp.get("/contratos/<int:id_contrato>/obligaciones")
@requiere_roles(COMISIONADO_CONTRATISTA)
def listar_obligaciones(id_contrato):
    documento = get_jwt_identity()
    try:
        with get_connection() as connection:
            contrato = obtener_contrato_para_operacion(
                connection, documento, id_contrato
            )
            if contrato is None:
                return {"mensaje": "Contrato no encontrado"}, 404
            obligaciones = connection.execute(
                """
                SELECT id_obligacion, descripcion
                  FROM obligaciones
                 WHERE id_contrato = %s
                 ORDER BY id_obligacion
                """,
                (id_contrato,),
            ).fetchall()
    except psycopg.Error:
        return {"mensaje": "No fue posible consultar las obligaciones"}, 503

    return {
        "obligaciones": [dict(row) for row in obligaciones]
    }, 200


@perfil_bp.put("/contratos/<int:id_contrato>/obligaciones")
@requiere_roles(COMISIONADO_CONTRATISTA)
def reemplazar_obligaciones(id_contrato):
    documento = get_jwt_identity()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {"mensaje": "Debe enviar un objeto JSON"}, 400

    error = reject_unknown_fields(payload, {"obligaciones"})
    if error:
        return error
    obligaciones = payload.get("obligaciones")
    if not isinstance(obligaciones, list):
        return {
            "mensaje": "El campo obligaciones debe ser una lista"
        }, 400
    if len(obligaciones) > 100:
        return {
            "mensaje": "No se permiten más de 100 obligaciones"
        }, 400

    descripciones = []
    for index, obligacion in enumerate(obligaciones):
        if not isinstance(obligacion, dict):
            return {
                "mensaje": f"La obligación {index + 1} debe ser un objeto"
            }, 400
        error = reject_unknown_fields(obligacion, {"descripcion"})
        if error:
            return error
        if "descripcion" not in obligacion:
            return {
                "mensaje": (
                    f"La obligación {index + 1} requiere descripcion"
                )
            }, 400
        error_message = valid_text(
            obligacion["descripcion"], "descripcion", 10000
        )
        if error_message:
            return {"mensaje": error_message}, 400
        descripciones.append(obligacion["descripcion"].strip())

    try:
        with get_connection() as connection:
            contrato = obtener_contrato_para_operacion(
                connection, documento, id_contrato
            )
            if contrato is None:
                return {"mensaje": "Contrato no encontrado"}, 404

            try:
                connection.execute(
                    "DELETE FROM obligaciones WHERE id_contrato = %s",
                    (id_contrato,),
                )
                for descripcion in descripciones:
                    connection.execute(
                        """
                        INSERT INTO obligaciones
                            (id_contrato, descripcion)
                        VALUES (%s, %s)
                        """,
                        (id_contrato, descripcion),
                    )
                connection.commit()
            except psycopg.Error:
                connection.rollback()
                raise
    except psycopg.Error:
        return {"mensaje": "No fue posible actualizar las obligaciones"}, 503

    return {"mensaje": "Obligaciones actualizadas correctamente"}, 200
