from flask import Blueprint

auth_bp = Blueprint("auth", __name__,url_prefix="/auth") # pegano o blueprint do app/__init__ lá para padronizar

from app.auth import routes