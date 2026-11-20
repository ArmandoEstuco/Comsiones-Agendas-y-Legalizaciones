from collections.abc import Callable
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


COMISIONADO_CONTRATISTA = "Comisionado contratista"
COMISIONADO_FUNCIONARIO = "Comisionado funcionario"
SUPERVISOR_DEL_CONTRATO = "Supervisor del contrato"
AREA_DE_VIATICOS = "Área de viáticos"
SUBDIRECTOR_DEL_CENTRO = "Subdirector del centro"

ROLES_OFICIALES = (
    COMISIONADO_CONTRATISTA,
    COMISIONADO_FUNCIONARIO,
    SUPERVISOR_DEL_CONTRATO,
    AREA_DE_VIATICOS,
    SUBDIRECTOR_DEL_CENTRO,
)


def requiere_roles(*roles: str) -> Callable:
    roles_desconocidos = set(roles) - set(ROLES_OFICIALES)
    if roles_desconocidos:
        raise ValueError(
            "Roles no oficiales: " + ", ".join(sorted(roles_desconocidos))
        )

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt().get("rol") not in roles:
                return jsonify({"mensaje": "Sin permiso"}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator
