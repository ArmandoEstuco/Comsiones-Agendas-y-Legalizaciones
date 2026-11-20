import os
from uuid import uuid4

from flask import Blueprint, current_app, request
from PIL import Image, UnidentifiedImageError

from ..utils.permisos import SUBDIRECTOR_DEL_CENTRO, requiere_roles


firmas_bp = Blueprint("firmas", __name__)
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}


@firmas_bp.post("/<int:id_agenda>/firmas")
@requiere_roles(SUBDIRECTOR_DEL_CENTRO)
def subir_firma(id_agenda):
    archivo = request.files.get("archivo")
    if archivo is None or archivo.filename == "":
        return {
            "mensaje": "Debe enviar una imagen en el campo archivo"
        }, 400

    archivo.stream.seek(0, os.SEEK_END)
    file_size = archivo.stream.tell()
    archivo.stream.seek(0)

    if file_size > current_app.config["MAX_SIGNATURE_SIZE"]:
        return {
            "mensaje": "La imagen supera el tamaño máximo de 1 MB"
        }, 413

    try:
        with Image.open(archivo.stream) as image:
            image_format = image.format
            image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError):
        return {
            "mensaje": "Solo se permiten imágenes PNG, JPG o JPEG"
        }, 415

    if image_format not in ALLOWED_IMAGE_FORMATS:
        return {
            "mensaje": "Solo se permiten imágenes PNG, JPG o JPEG"
        }, 415

    archivo.stream.seek(0)
    extension = ".jpg" if image_format == "JPEG" else ".png"
    upload_folder = current_app.config["FIRMAS_UPLOAD_FOLDER"]
    os.makedirs(upload_folder, mode=0o700, exist_ok=True)

    filename = f"{uuid4().hex}{extension}"
    destination = os.path.join(upload_folder, filename)

    try:
        with open(destination, "xb") as destination_file:
            while True:
                chunk = archivo.stream.read(1024 * 1024)
                if not chunk:
                    break
                destination_file.write(chunk)
    except FileExistsError:
        return {
            "mensaje": "No fue posible guardar la imagen"
        }, 500
    except OSError:
        return {
            "mensaje": "No fue posible guardar la imagen"
        }, 500

    return {
        "mensaje": "Firma guardada correctamente",
        "archivo": filename,
        "id_agenda": id_agenda,
        "asociada_a_base_datos": False,
    }, 201
