from flask_mail import Message

from app.extensions import mail


def enviar_email(destinatario, assunto, mensagem, html=None):
    msg = Message(
        subject=assunto,
        recipients=[destinatario],
    )

    msg.body = mensagem

    if html:
        msg.html = html

    mail.send(msg)