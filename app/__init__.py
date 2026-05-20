from flask import Flask

from app.config import Config
from app.extensions import db, migrate, login_manager, bcrypt, mail
from app.financeiro.agendador import iniciar_agendador

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = ("Faça login para acessar esta página.")
    login_manager.login_message_category = "warning"

    from app.utils.formatters import registrar_filtros
    registrar_filtros(app)

    from app.auth import auth_bp
    from app.main import main_bp
    from app.financeiro import financeiro_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(financeiro_bp)

    iniciar_agendador()

    return app
