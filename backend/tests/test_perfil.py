from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from flask_jwt_extended import create_access_token

from app.utils.permisos import (
    COMISIONADO_CONTRATISTA,
    COMISIONADO_FUNCIONARIO,
)


def make_token(app, rol=COMISIONADO_CONTRATISTA):
    with app.app_context():
        return create_access_token(
            identity="DEMO-S3-001",
            additional_claims={"rol": rol},
        )


def auth_headers(app, rol=COMISIONADO_CONTRATISTA):
    return {
        "Authorization": f"Bearer {make_token(app, rol)}"
    }


@contextmanager
def mocked_connection(connection):
    yield connection


def test_perfil_sin_jwt_es_rechazado(client):
    response = client.get("/api/perfil")

    assert response.status_code == 401


def test_perfil_con_rol_incorrecto_es_rechazado(app, client):
    response = client.get(
        "/api/perfil",
        headers=auth_headers(app, COMISIONADO_FUNCIONARIO),
    )

    assert response.status_code == 403


def test_get_perfil_devuelve_datos_del_documento_jwt(app, client):
    connection = MagicMock()
    cursor = connection.execute.return_value
    cursor.fetchone.return_value = {
        "documento_usuario": "DEMO-S3-001",
        "tipo_documento": "CC",
        "nombres": "Prueba",
        "apellidos": "Contratista",
        "correo": "prueba.s1.01@sena.edu.co",
        "estado": "activo",
        "nombre_rol": "Comisionado contratista",
    }

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.get(
            "/api/perfil",
            headers=auth_headers(app),
        )

    assert response.status_code == 200
    assert response.get_json()["perfil"]["documento_usuario"] == "DEMO-S3-001"


def test_patch_perfil_actualiza_y_hace_commit(app, client):
    connection = MagicMock()
    update_result = connection.execute.return_value
    update_result.rowcount = 1

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.patch(
            "/api/perfil",
            headers=auth_headers(app),
            json={"nombres": "Nuevo", "correo": "nuevo@sena.edu.co"},
        )

    assert response.status_code == 200
    connection.commit.assert_called_once()


def test_patch_perfil_rechaza_campo_desconocido(app, client):
    response = client.patch(
        "/api/perfil",
        headers=auth_headers(app),
        json={"documento_usuario": "OTRO"},
    )

    assert response.status_code == 400
    assert "Campos no permitidos" in response.get_json()["mensaje"]


def test_patch_perfil_rechaza_correo_invalido(app, client):
    response = client.patch(
        "/api/perfil",
        headers=auth_headers(app),
        json={"correo": "correo-invalido"},
    )

    assert response.status_code == 400


def test_listar_contratos_no_incluye_extranos(app, client):
    connection = MagicMock()
    connection.execute.return_value.fetchall.return_value = [
        {
            "id_contrato": 10,
            "numero_contrato": "CT-10",
            "anio": 2026,
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "objeto_contractual": "Servicio",
        }
    ]

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.get(
            "/api/perfil/contratos",
            headers=auth_headers(app),
        )

    assert response.status_code == 200
    assert len(response.get_json()["contratos"]) == 1


def test_contrato_ajeno_responde_404(app, client):
    connection = MagicMock()
    connection.execute.return_value.fetchone.return_value = None

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.get(
            "/api/perfil/contratos/999",
            headers=auth_headers(app),
        )

    assert response.status_code == 404
    assert response.get_json()["mensaje"] == "Contrato no encontrado"


def test_patch_contrato_actualiza_y_hace_commit(app, client):
    connection = MagicMock()
    connection.execute.return_value.fetchone.return_value = {
        "id_contrato": 10,
        "numero_contrato": "CT-10",
        "anio": 2026,
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31",
        "objeto_contractual": "Servicio",
    }

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.patch(
            "/api/perfil/contratos/10",
            headers=auth_headers(app),
            json={
                "numero_contrato": "CT-10-NUEVO",
                "objeto_contractual": "Objeto nuevo",
            },
        )

    assert response.status_code == 200
    connection.commit.assert_called_once()


def test_patch_contrato_rechaza_fecha_invertida(app, client):
    connection = MagicMock()
    connection.execute.return_value.fetchone.return_value = {
        "id_contrato": 10,
        "numero_contrato": "CT-10",
        "anio": 2026,
        "fecha_inicio": "2026-12-31",
        "fecha_fin": "2026-12-31",
        "objeto_contractual": "Servicio",
    }

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.patch(
            "/api/perfil/contratos/10",
            headers=auth_headers(app),
            json={
                "fecha_inicio": "2026-12-31",
                "fecha_fin": "2026-01-01",
            },
        )

    assert response.status_code == 400
    connection.commit.assert_not_called()


def test_patch_contrato_rechaza_campos_desconocidos(app, client):
    response = client.patch(
        "/api/perfil/contratos/10",
        headers=auth_headers(app),
        json={"documento_supervisor": "OTRO"},
    )

    assert response.status_code == 400


def test_listar_obligaciones_solo_para_contrato_propio(app, client):
    connection = MagicMock()
    cursor = connection.execute.return_value
    cursor.fetchone.return_value = {
        "id_contrato": 10,
        "numero_contrato": "CT-10",
        "anio": 2026,
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31",
        "objeto_contractual": "Servicio",
    }
    cursor.fetchall.return_value = [
        {"id_obligacion": 1, "descripcion": "Obligación uno"}
    ]

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.get(
            "/api/perfil/contratos/10/obligaciones",
            headers=auth_headers(app),
        )

    assert response.status_code == 200
    assert len(response.get_json()["obligaciones"]) == 1


def test_put_obligaciones_reemplaza_y_hace_commit(app, client):
    connection = MagicMock()
    cursor = connection.execute.return_value
    cursor.fetchone.return_value = {
        "id_contrato": 10,
        "numero_contrato": "CT-10",
        "anio": 2026,
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31",
        "objeto_contractual": "Servicio",
    }

    with patch(
        "app.routes.perfil.get_connection",
        side_effect=lambda: mocked_connection(connection),
    ):
        response = client.put(
            "/api/perfil/contratos/10/obligaciones",
            headers=auth_headers(app),
            json={
                "obligaciones": [
                    {"descripcion": "Obligación nueva"}
                ]
            },
        )

    assert response.status_code == 200
    connection.commit.assert_called_once()


def test_put_obligaciones_rechaza_descripcion_vacia(app, client):
    response = client.put(
        "/api/perfil/contratos/10/obligaciones",
        headers=auth_headers(app),
        json={"obligaciones": [{"descripcion": "  "}]},
    )

    assert response.status_code == 400


def test_put_obligaciones_rechaza_id_obligacion(app, client):
    response = client.put(
        "/api/perfil/contratos/10/obligaciones",
        headers=auth_headers(app),
        json={
            "obligaciones": [
                {"id_obligacion": 1, "descripcion": "Texto"}
            ]
        },
    )

    assert response.status_code == 400
