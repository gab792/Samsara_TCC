from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from app.auth import auth_bp
from app.auth.forms import RegisterForm, LoginForm
from app.auth.services import criar_usuario, logar_usuario


@auth_bp.route("/cadastro/", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = criar_usuario(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        login_user(user, remember=True)
        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("financeiro.dashboard"))

    return render_template("auth/cadastro.html", form=form)


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = logar_usuario(
            email=form.email.data,
            password=form.password.data,
        )

        if user:
            login_user(user, remember=True)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("financeiro.dashboard"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Logout realizado.", "success")
    return redirect(url_for("auth.login"))