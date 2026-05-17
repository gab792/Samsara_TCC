from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class LancamentoForm(FlaskForm):
    categoria = SelectField(
        "Categoria",
        coerce=int,
        validators=[Optional()],
    )

    favorecido = StringField(
        "Favorecido / Fornecedor",
        validators=[
            Optional(),
            Length(max=150, message="O favorecido deve ter no máximo 150 caracteres."),
        ],
    )


    valor = DecimalField(
        "Valor (R$)",
        places=2,
        validators=[
            DataRequired(message="Informe o valor."),
            NumberRange(min=0.01, message="O valor deve ser maior que zero."),
        ],
    )

    tipo_custo = SelectField(
        "Tipo de Custo",
        choices=[
            ("variavel", "Variável"),
            ("fixo", "Fixo"),
        ],
        validators=[
            DataRequired(message="Selecione o tipo de custo."),
        ],
    )

    conta_origem = SelectField(
        "Conta de Origem",
        choices=[
            ("", "Selecione"),
            ("dinheiro", "Dinheiro"),
            ("stone", "Stone"),
            ("itau", "Itaú"),
            ("outro", "Outro"),
        ],
        validators=[Optional()],
    )

    forma_pagamento = SelectField(
        "Forma de Pagamento",
        choices=[
            ("", "Selecione"),
            ("pix", "Pix"),
            ("debito", "Débito"),
            ("credito", "Crédito"),
            ("boleto", "Boleto"),
            ("outro", "Outro"),
        ],
        validators=[Optional()],
    )

    status = SelectField(
        "Status",
        choices=[
            ("pendente", "Pendente"),
            ("pago", "Pago"),
        ],
        validators=[
            DataRequired(message="Selecione o status."),
        ],
    )

    data_lancamento = DateField(
        "Data do Lançamento",
        default=date.today,
        validators=[
            DataRequired(message="Informe a data do lançamento."),
        ],
    )

    data_vencimento = DateField(
        "Data de Vencimento",
        validators=[Optional()],
    )

    data_pagamento = DateField(
        "Data de pagamento",
        validators=[Optional()],
    )

    observacao = TextAreaField(
        "Observação",
        validators=[
            Optional(),
            Length(max=500, message="A observação deve ter no máximo 500 caracteres."),
        ],
    )

    btnSubmit = SubmitField("Salvar lançamento")

class CategoriaForm(FlaskForm):
    nome = StringField(
        "Nome da Categoria",
        validators=[
            DataRequired(message="Informe o nome da categoria."),
            Length(max=80, message="O nome deve ter no máximo 80 caracteres."),
        ],
        render_kw={
            "placeholder": "Ex: Aluguel, Energia, Mercadorias..."
        },
    )

    btnSubmit = SubmitField("Salvar categoria")
