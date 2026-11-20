from flask import Blueprint, jsonify

from ..utils.permisos import SUPERVISOR_DEL_CONTRATO, requiere_roles


contratos_bp = Blueprint("contratos", __name__)


@contratos_bp.post("")
@requiere_roles(SUPERVISOR_DEL_CONTRATO)
def crear_contrato():
    return jsonify(
        {
            "mensaje": (
                "Operación de creación de contratos todavía no implementada"
            )
        }
    ), 501
