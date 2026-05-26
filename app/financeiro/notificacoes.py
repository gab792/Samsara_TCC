from collections import defaultdict
from datetime import date, timedelta

from app.models import LancamentoFinanceiro
from app.financeiro.email_service import enviar_email


def buscar_lancamentos_vencendo_amanha(user_id=None):
    amanha = date.today() + timedelta(days=1)

    query = LancamentoFinanceiro.query.filter(
        LancamentoFinanceiro.status == "pendente",
        LancamentoFinanceiro.data_vencimento == amanha,
    )

    if user_id is not None:
        query = query.filter(
            LancamentoFinanceiro.user_id == user_id
        )

    return query.order_by(
        LancamentoFinanceiro.data_vencimento.asc(),
        LancamentoFinanceiro.valor.desc(),
    ).all()


def formatar_moeda_email(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def montar_mensagem_texto(usuario, lancamentos):
    nome_usuario = usuario.username.title()

    linhas = []

    for lancamento in lancamentos:
        favorecido = (
            lancamento.favorecido.strip().title()
            if lancamento.favorecido
            else "Não informado"
        )
        valor = formatar_moeda_email(lancamento.valor)
        linhas.append(
            f"- {favorecido} | {valor} | Vence amanhã"
        )

    lista_lancamentos = "\n".join(linhas)

    return f"""
Olá, {nome_usuario}!

Você possui {len(lancamentos)} conta(s) com vencimento para amanhã:

{lista_lancamentos}

Acesse a agenda financeira do sistema para conferir os detalhes.

Este é um alerta automático de vencimento.
"""


def montar_mensagem_html(usuario, lancamentos):
    nome_usuario = usuario.username.title()

    linhas_tabela = ""

    for lancamento in lancamentos:
        favorecido = (
            lancamento.favorecido.strip().title()
            if lancamento.favorecido
            else "Não informado"
        )
        valor = formatar_moeda_email(lancamento.valor)
        linhas_tabela += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">
                    {favorecido}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">
                    {valor}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">
                    Amanhã
                </td>
            </tr>
        """

    return f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 24px;">
        <div style="max-width: 620px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb;">
            
            <div style="background-color: #d54e00; color: white; padding: 20px 24px;">
                <h2 style="margin: 0; font-size: 22px;">Alerta de vencimento</h2>
                <p style="margin: 6px 0 0; font-size: 14px;">
                    Você possui conta(s) com vencimento para amanhã.
                </p>
            </div>

            <div style="padding: 24px;">
                <p style="margin-top: 0; color: #111827;">
                    Olá, <strong>{nome_usuario}</strong>!
                </p>

                <p style="color: #374151; line-height: 1.5;">
                    Identificamos <strong>{len(lancamentos)} conta(s)</strong> pendente(s) com vencimento para amanhã.
                </p>

                <table style="width: 100%; border-collapse: collapse; margin-top: 18px; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #f9fafb;">
                            <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">Favorecido</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 1px solid #e5e7eb;">Valor</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 1px solid #e5e7eb;">Vencimento</th>
                        </tr>
                    </thead>

                    <tbody>
                        {linhas_tabela}
                    </tbody>
                </table>

                <p style="color: #374151; line-height: 1.5; margin-top: 22px;">
                    Acesse a agenda financeira do sistema para conferir os detalhes e registrar o pagamento.
                </p>

                <p style="margin-top: 24px; color: #6b7280; font-size: 12px;">
                    Este é um alerta automático de vencimento enviado pelo sistema Samsara.
                </p>
            </div>
        </div>
    </div>
    """


def enviar_alertas_vencimento(user_id=None):
    lancamentos = buscar_lancamentos_vencendo_amanha(
        user_id=user_id
    )

    if not lancamentos:
        return {
            "emails_enviados": 0,
            "lancamentos_encontrados": 0,
        }

    lancamentos_por_usuario = defaultdict(list)

    for lancamento in lancamentos:
        lancamentos_por_usuario[lancamento.usuario].append(lancamento)

    emails_enviados = 0

    for usuario, lancamentos_usuario in lancamentos_por_usuario.items():
        mensagem_texto = montar_mensagem_texto(
            usuario=usuario,
            lancamentos=lancamentos_usuario,
        )

        mensagem_html = montar_mensagem_html(
            usuario=usuario,
            lancamentos=lancamentos_usuario,
        )

        assunto = (
            f"Alerta de vencimento: "
            f"{len(lancamentos_usuario)} conta(s) vencem amanhã"
        )

        enviar_email(
            destinatario=usuario.email,
            assunto=assunto,
            mensagem=mensagem_texto,
            html=mensagem_html,
        )

        emails_enviados += 1

    return {
        "emails_enviados": emails_enviados,
        "lancamentos_encontrados": len(lancamentos),
    }


def verificar_vencimentos(app):
    with app.app_context():
        enviar_alertas_vencimento()