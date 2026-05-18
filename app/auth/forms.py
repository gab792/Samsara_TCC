from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models import User


class RegisterForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[
        DataRequired(message="Informe um nome de usuário."),
        Length(min=3, max=30, message="O nome de usuário deve ter entre 3 e 30 caracteres.")
    ])
    email = StringField("Email", validators=[
        DataRequired(message="Informe seu e-mail."),
        Email(message="Endereço de e-mail inválido.")
    ])
    password = PasswordField("Senha", validators=[
        DataRequired(message="Informe uma senha."),
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
    ])
    confirma_pass = PasswordField("Confirme a senha", validators=[
        DataRequired(message="Confirme sua senha."),
        EqualTo("password", message="As senhas não coincidem.")
    ])

    btnSubmit = SubmitField("Cadastrar")

    # validações proprias que verifica se já existe email ou usuario cadastrado
    def validate_username(self, username):
        username_normalized = username.data.strip().lower()
        user = User.query.filter_by(username=username_normalized).first()
        if user:
            raise ValidationError("Nome de usuário já cadastrado.")

    def validate_email(self, email):
        email_normalized = email.data.strip().lower()
        user = User.query.filter_by(email=email_normalized).first()
        if user:
            raise ValidationError("E-mail já cadastrado.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    btnSubmit = SubmitField("Entrar")
