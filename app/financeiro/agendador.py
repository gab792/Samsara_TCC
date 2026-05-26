from apscheduler.schedulers.background import BackgroundScheduler
from app.financeiro.notificacoes import verificar_vencimentos


def iniciar_agendador(app):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=verificar_vencimentos,
        trigger="cron",
        hour=8,
        minute=0,
        args=[app],
    )

    scheduler.start()