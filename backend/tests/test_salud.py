from unittest.mock import patch


def test_salud(client):
    with patch("app.routes.salud.get_connection") as get_connection:
        connection = get_connection.return_value.__enter__.return_value
        response = client.get("/api/salud")

    assert response.status_code == 200
    assert response.get_json() == {
        "estado": "ok",
        "base_datos": "conectada",
    }
    connection.execute.assert_called_once_with("SELECT 1")
