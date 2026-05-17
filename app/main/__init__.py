from flask import Blueprint

main_bp = Blueprint("main", __name__) # pegano o blueprint do app/__init__ lá para padronizar

from app.main import routes