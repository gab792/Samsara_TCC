from app.extensions import db, bcrypt
from app.models import User

def criar_usuario(username, email, password):
    # tratando da normalização de user e email; criando hash
    username_normalizado = username.strip().lower()
    email_normalizado = email.strip().lower()

    senha_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    
    # criando e salvando User no banco
    user = User(
        username=username_normalizado,
        email=email_normalizado,
        password=senha_hash,
    )
    
    db.session.add(user)
    db.session.commit()
    return user


def logar_usuario(email, password):
    email_normalizado = email.strip().lower()

    user = User.query.filter_by(
        email=email_normalizado
    ).first()

    if user and bcrypt.check_password_hash(
        user.password,
        password
    ):
        return user

    return None
