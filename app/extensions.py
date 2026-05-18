from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# login_manager.login_view = 'login' > # se o usuario não tiver logado redireciona para essa página (preciso ver como faz)
bcrypt = Bcrypt()
