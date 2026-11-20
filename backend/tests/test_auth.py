from unittest.mock import patch

from flask import jsonify

from app.utils.permisos import (
    requiere_roles,
)

def test_login_rejects_invalid_credentials(client):
    with patch("app.routes.auth.authenticate_user", return_value=None):
        response = client.post(
            "/api/auth/login",
            json={
                "correo": "usuario@ejemplo.com",
                "contrasena": "incorrecta",
            },
        )

    assert response.status_code == 401
    assert "token" not in response.get_json()


def test_login_returns_jwt_with_role(client):
    user = {
        "id": "DEMO-S1-001",
        "correo": "prueba.s1.01@sena.edu.co",
        "rol": "Comisionado contratista",
    }
    with patch("app.routes.auth.authenticate_user", return_value=user):
        response = client.post(
            "/api/auth/login",
            json={
                "correo": user["correo"],
                "contrasena": "SenaDemo2026!",
            },
        )

    assert response.status_code == 200
    assert response.get_json()["usuario"]["rol"] == user["rol"]
    assert response.get_json()["token"]


def test_festivos_rejects_invalid_year(client):
    response = client.get("/api/dias-festivos?anio=no-es-un-anio")

    assert response.status_code == 400


def test_protected_route_rejects_invalid_token(app):
    @app.get("/api/protegida")
    @requiere_roles("Comisionado funcionario")
    def protected():
        return jsonify({"ok": True})

    response = app.test_client().get(
        "/api/protegida",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 422
