from apscheduler.schedulers.background import BackgroundScheduler
from app.financeiro.notificacoes import verificar_vencimentos

def iniciar_agendador():

    scheduler = BackgroundScheduler()

    # ⏰ isso significa: roda a cada 1 hora
    scheduler.add_job(
        func=verificar_vencimentos,
        trigger="interval",
        minutes=1
    )

    scheduler.start()