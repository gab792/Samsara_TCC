from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.main import main_bp


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("financeiro.dashboard"))

    return redirect(url_for("auth.login"))


@main_bp.route("/perfil/")
@login_required
def perfil():
    return render_template("main/perfil.html")
