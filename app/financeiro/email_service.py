from flask_mail import Message

from app.extensions import mail


def enviar_email(destinatario, assunto, mensagem):

    msg = Message(
        subject=assunto,
        recipients=[destinatario]
    )

    msg.body = mensagem

    mail.send(msg)