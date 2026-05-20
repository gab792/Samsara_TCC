from datetime import date, timedelta

from app.models import LancamentoFinanceiro
from app.financeiro.email_service import enviar_email


def verificar_vencimentos():

    amanha = date.today() + timedelta(days=1)

    lancamentos = LancamentoFinanceiro.query.filter_by(
        status="pendente"
    ).all()

    for lancamento in lancamentos:

        if lancamento.data_vencimento == amanha:

            usuario = lancamento.usuario

            mensagem = f"""
Olá, {usuario.username}!

Sua fatura no valor de R$ {lancamento.valor}
vence amanhã.

Favorecido: {lancamento.favorecido}

Não esqueça do pagamento 💸
"""

            enviar_email(
                destinatario=usuario.email,
                assunto="Fatura próxima do vencimento",
                mensagem=mensagem
            )