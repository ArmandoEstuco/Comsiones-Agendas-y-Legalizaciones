from io import BytesIO

from PIL import Image
from flask_jwt_extended import create_access_token

from app.utils.permisos import (
    COMISIONADO_CONTRATISTA,
    SUBDIRECTOR_DEL_CENTRO,
)


def make_token(app, rol):
    with app.app_context():
        return create_access_token(
            identity="DEMO-S3-001",
            additional_claims={"rol": rol},
        )


def image_bytes(image_format):
    output = BytesIO()
    Image.new("RGB", (100, 100), color="white").save(output, format=image_format)
    output.seek(0)
    return output


def post_signature(client, app, tmp_path, payload, rol=SUBDIRECTOR_DEL_CENTRO, token=True):
    app.config["FIRMAS_UPLOAD_FOLDER"] = str(tmp_path)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {make_token(app, rol)}"
    return client.post(
        "/api/agendas/123/firmas",
        data=payload,
        headers=headers,
        content_type="multipart/form-data",
    )


def test_subida_png_valida(app, client, tmp_path):
    response = post_signature(
        client,
        app,
        tmp_path,
        {"archivo": (image_bytes("PNG"), "firma.png")},
    )

    assert response.status_code == 201
    assert response.get_json()["asociada_a_base_datos"] is False


def test_subida_jpg_valida(app, client, tmp_path):
    response = post_signature(
        client,
        app,
        tmp_path,
        {"archivo": (image_bytes("JPEG"), "firma.jpg")},
    )

    assert response.status_code == 201


def test_pdf_es_rechazado(app, client, tmp_path):
    pdf = BytesIO(b"%PDF-1.7\n%%EOF")
    response = post_signature(
        client,
        app,
        tmp_path,
        {"archivo": (pdf, "firma.pdf")},
    )

    assert response.status_code == 415
    assert "Solo se permiten" in response.get_json()["mensaje"]


def test_imagen_de_3_mb_es_rechazada(app, client, tmp_path):
    large_image = image_bytes("JPEG")
    padded = large_image.getvalue() + (b"0" * (3 * 1024 * 1024))
    response = post_signature(
        client,
        app,
        tmp_path,
        {"archivo": (BytesIO(padded), "firma.jpg")},
    )

    assert response.status_code == 413
    assert "1 MB" in response.get_json()["mensaje"]


def test_solicitud_sin_archivo_es_rechazada(app, client, tmp_path):
    response = post_signature(client, app, tmp_path, {}, token=True)

    assert response.status_code == 400
    assert "campo archivo" in response.get_json()["mensaje"]


def test_solicitud_sin_jwt_es_rechazada(app, client, tmp_path):
    response = post_signature(
        client,
        app,
        tmp_path,
        {"archivo": (image_bytes("PNG"), "firma.png")},
        token=False,
    )

    assert response.status_code == 401


def test_rol_incorrecto_es_rechazado(app, client, tmp_path):
    response = post_signature(
        client,
        app,
        tmp_path,
        {"archivo": (image_bytes("PNG"), "firma.png")},
        rol=COMISIONADO_CONTRATISTA,
    )

    assert response.status_code == 403
    assert response.get_json() == {"mensaje": "Sin permiso"}
