from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from .config import Config
from .extensions import jwt, limiter
from .routes.auth import auth_bp
from .routes.contratos import contratos_bp
from .routes.festivos import festivos_bp
from .routes.firmas import firmas_bp
from .routes.perfil import perfil_bp
from .routes.salud import salud_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    limiter.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(salud_bp, url_prefix="/api/salud")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(contratos_bp, url_prefix="/api/contratos")
    app.register_blueprint(festivos_bp, url_prefix="/api/dias-festivos")
    app.register_blueprint(firmas_bp, url_prefix="/api/agendas")
    app.register_blueprint(perfil_bp, url_prefix="/api/perfil")

    @app.errorhandler(404)
    def handle_not_found(_error):
        return {"mensaje": "Ruta no encontrada"}, 404

    @app.errorhandler(429)
    def handle_rate_limit(_error):
        return {"mensaje": "Demasiados intentos. Intente nuevamente más tarde."}, 429

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_too_large(_error):
        return {
            "mensaje": "La imagen supera el tamaño máximo de 1 MB"
        }, 413

    return app
