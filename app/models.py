from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import date


# LOGIN
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    telefone = db.Column(db.String(20))

    password = db.Column(db.String(200), nullable=False)

    categorias = db.relationship(
        "CategoriaFinanceira",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    lancamentos = db.relationship(
        "LancamentoFinanceiro",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )


# FINANCEIRO
class CategoriaFinanceira(db.Model): # A categoria serve para agrupar e gerar relatório.
    __table_args__ = (db.UniqueConstraint("nome", "user_id", name="uq_categoria_nome_user"),) # restrição para evitar duplicadas, não repetir categorias
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class LancamentoFinanceiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    favorecido = db.Column(db.String(150), nullable=True) # Forncedores
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_custo = db.Column(db.String(20), nullable=False, default="variável")
    conta_origem = db.Column(db.String(50), nullable=True)
    forma_pagamento = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pendente")
    data_lancamento = db.Column(db.Date, nullable=False, default=date.today)
    data_vencimento = db.Column(db.Date, nullable=True)
    data_pagamento = db.Column(db.Date, nullable=True)
    observacao = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria_financeira.id"), nullable=False)
    categoria = db.relationship("CategoriaFinanceira", backref="lancamentos")
