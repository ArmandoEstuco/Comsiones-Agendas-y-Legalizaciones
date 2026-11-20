from flask_jwt_extended import create_access_token

from app.utils.permisos import (
    COMISIONADO_CONTRATISTA,
    COMISIONADO_FUNCIONARIO,
    SUPERVISOR_DEL_CONTRATO,
)


def make_token(app, rol):
    with app.app_context():
        return create_access_token(
            identity="DEMO-S2-001",
            additional_claims={"rol": rol},
        )


def test_comisionado_contratista_recibe_sin_permiso(app, client):
    token = make_token(app, COMISIONADO_CONTRATISTA)

    response = client.post(
        "/api/contratos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json() == {"mensaje": "Sin permiso"}


def test_comisionado_funcionario_recibe_sin_permiso(app, client):
    token = make_token(app, COMISIONADO_FUNCIONARIO)

    response = client.post(
        "/api/contratos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json() == {"mensaje": "Sin permiso"}


def test_supervisor_supera_autorizacion_y_recibe_501(app, client):
    token = make_token(app, SUPERVISOR_DEL_CONTRATO)

    response = client.post(
        "/api/contratos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 501
    assert "no implementada" in response.get_json()["mensaje"]


def test_peticion_sin_token_es_rechazada(client):
    response = client.post("/api/contratos")

    assert response.status_code == 401
