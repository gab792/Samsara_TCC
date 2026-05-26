from datetime import date, timedelta
from calendar import monthrange
from sqlalchemy import func

from app.extensions import db
from app.models import LancamentoFinanceiro, CategoriaFinanceira


# GRÁFICO DO DASHBOARD
def obter_gastos_mensais_ano(user_id, ano=None):
    hoje = date.today()

    if ano is None:
        ano = hoje.year

    labels = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ]

    valores = []

    for mes in range(1, 13):
        primeiro_dia = date(ano, mes, 1)
        ultimo_dia = date(ano, mes, monthrange(ano, mes)[1],)

        total_mes = (
            db.session.query(db.func.sum(LancamentoFinanceiro.valor))
            .filter(
                LancamentoFinanceiro.user_id == user_id,
                LancamentoFinanceiro.status == "pago",
                LancamentoFinanceiro.data_pagamento.isnot(None),
                LancamentoFinanceiro.data_pagamento >= primeiro_dia,
                LancamentoFinanceiro.data_pagamento <= ultimo_dia,
            )
            .scalar()
            or 0
        )

        valores.append(float(total_mes))

    return {"labels": labels, "valores": valores, "ano": ano,}


# RELATÓRIO
def obter_relatorio_mensal(user_id, mes=None, ano=None):
    hoje = date.today()

    mes = int(mes) if mes else hoje.month
    ano = int(ano) if ano else hoje.year

    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(
        ano,
        mes,
        monthrange(ano, mes)[1],
    )

    lancamentos = (
        LancamentoFinanceiro.query
        .filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.data_lancamento >= primeiro_dia,
            LancamentoFinanceiro.data_lancamento <= ultimo_dia,
        )
        .order_by(LancamentoFinanceiro.data_lancamento.desc())
        .all()
    )

    total_pago = sum(
        lancamento.valor
        for lancamento in lancamentos
        if lancamento.status == "pago"
    )

    total_pendente = sum(
        lancamento.valor
        for lancamento in lancamentos
        if lancamento.status == "pendente"
    )

    total_geral = sum(
        lancamento.valor
        for lancamento in lancamentos
    )

    total_por_categoria = {}

    for lancamento in lancamentos:
        categoria_nome = (
            lancamento.categoria.nome
            if lancamento.categoria
            else "Sem categoria"
        )

        total_por_categoria[categoria_nome] = (
            total_por_categoria.get(categoria_nome, 0)
            + lancamento.valor
        )

    total_por_pagamento = {}

    for lancamento in lancamentos:
        forma = lancamento.forma_pagamento or "Não informado"

        total_por_pagamento[forma] = (
            total_por_pagamento.get(forma, 0)
            + lancamento.valor
        )

    return {
        "mes": mes,
        "ano": ano,
        "lancamentos": lancamentos,
        "total_pago": total_pago,
        "total_pendente": total_pendente,
        "total_geral": total_geral,
        "total_por_categoria": total_por_categoria,
        "total_por_pagamento": total_por_pagamento,
    }


# AGENDA
def obter_agenda_financeira(user_id):
    hoje = date.today()
    proximos_7_dias = hoje + timedelta(days=7)
    proximos_30_dias = hoje + timedelta(days=30)

    vencidas = (
        LancamentoFinanceiro.query.filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
            LancamentoFinanceiro.data_vencimento.isnot(None),
            LancamentoFinanceiro.data_vencimento < hoje,
        )
        .order_by(LancamentoFinanceiro.data_vencimento.asc())
        .all()
    )

    vencem_hoje = (
        LancamentoFinanceiro.query.filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
            LancamentoFinanceiro.data_vencimento == hoje,
        )
        .order_by(LancamentoFinanceiro.valor.desc())
        .all()
    )

    proximos_7 = (
        LancamentoFinanceiro.query.filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
            LancamentoFinanceiro.data_vencimento.isnot(None),
            LancamentoFinanceiro.data_vencimento > hoje,
            LancamentoFinanceiro.data_vencimento <= proximos_7_dias,
        )
        .order_by(LancamentoFinanceiro.data_vencimento.asc())
        .all()
    )

    proximos_30 = (
        LancamentoFinanceiro.query.filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
            LancamentoFinanceiro.data_vencimento.isnot(None),
            LancamentoFinanceiro.data_vencimento > proximos_7_dias,
            LancamentoFinanceiro.data_vencimento <= proximos_30_dias,
        )
        .order_by(LancamentoFinanceiro.data_vencimento.asc())
        .all()
    )

    total_pendente = (
        db.session.query(db.func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
        )
        .scalar()
        or 0
    )

    return {
        "hoje": hoje,
        "vencidas": vencidas,
        "vencem_hoje": vencem_hoje,
        "proximos_7": proximos_7,
        "proximos_30": proximos_30,
        "total_pendente": total_pendente,
    }


# FILTRO LANÇAMENTOS
def listar_lancamentos_filtrados(user_id, status=None, mes=None, ano=None, categoria_id=None,):
    query = LancamentoFinanceiro.query.filter_by(user_id=user_id)

    if status in ["pendente", "pago"]:
        query = query.filter(LancamentoFinanceiro.status == status)

    if categoria_id and categoria_id != "0":
        query = query.filter(LancamentoFinanceiro.categoria_id == int(categoria_id))

    if ano:
        ano = int(ano)

        if mes:
            mes = int(mes)
            primeiro_dia = date(ano, mes, 1,)
            ultimo_dia = date(ano, mes, monthrange(ano, mes)[1],)

        else:
            primeiro_dia = date(ano, 1, 1,)
            ultimo_dia = date(ano, 12, 31,)

        query = query.filter(
            LancamentoFinanceiro.data_lancamento >= primeiro_dia,
            LancamentoFinanceiro.data_lancamento <= ultimo_dia,
        )

    lancamentos = (query.order_by(LancamentoFinanceiro.data_lancamento.desc()).all())

    total_somatorio = (
        sum(lancamento.valor for lancamento in lancamentos)
        if lancamentos
        else 0
    )

    return lancamentos, total_somatorio


# LANÇAMENTOS
def criar_lancamento(form, user_id):
    lancamento = LancamentoFinanceiro(
        user_id=user_id
    )

    preencher_lancamento_com_form(
        lancamento=lancamento,
        form=form
    )

    db.session.add(lancamento)
    db.session.commit()

    return lancamento

def preencher_lancamento_com_form(lancamento, form):
    lancamento.categoria_id = form.categoria.data

    lancamento.favorecido = (
        form.favorecido.data.strip()
        if form.favorecido.data
        else None
    )

    lancamento.valor = form.valor.data
    lancamento.tipo_custo = form.tipo_custo.data
    lancamento.conta_origem = form.conta_origem.data or None
    lancamento.forma_pagamento = form.forma_pagamento.data or None
    lancamento.status = form.status.data
    lancamento.data_lancamento = form.data_lancamento.data
    lancamento.data_vencimento = form.data_vencimento.data

    lancamento.observacao = (
        form.observacao.data.strip()
        if form.observacao.data
        else None
    )

    if lancamento.status == "pago":
        lancamento.data_pagamento = (
            form.data_pagamento.data
            if form.data_pagamento.data
            else date.today()
        )

    if lancamento.status == "pendente":
        lancamento.data_pagamento = None


def obter_resumo_dashboard(user_id):
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)

    total_mes = (
        db.session.query(db.func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pago",
            LancamentoFinanceiro.data_pagamento >= inicio_mes,
            LancamentoFinanceiro.data_pagamento <= hoje,
        )
        .scalar()
        or 0
    )

    total_pendente = (
        db.session.query(db.func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
        )
        .scalar()
        or 0
    )


    total_vencido = (
        db.session.query(db.func.sum(LancamentoFinanceiro.valor)).filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
            LancamentoFinanceiro.data_vencimento.isnot(None),
            LancamentoFinanceiro.data_vencimento < hoje,
        )
        .scalar()
        or 0
    )

    qtd_vencidas = (
        LancamentoFinanceiro.query.filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.status == "pendente",
            LancamentoFinanceiro.data_vencimento.isnot(None),
            LancamentoFinanceiro.data_vencimento < hoje,
        )
        .count()
    )

    qtd_lancamentos_mes = (
        LancamentoFinanceiro.query.filter(
            LancamentoFinanceiro.user_id == user_id,
            LancamentoFinanceiro.data_lancamento >= inicio_mes,
            LancamentoFinanceiro.data_lancamento <= hoje,
        )
        .count()
    )

    ultimos_lancamentos = (
        LancamentoFinanceiro.query.filter_by(user_id=user_id)
        .order_by(LancamentoFinanceiro.data_lancamento.desc())
        .limit(3)
        .all()
    )

    return {
        "total_mes": total_mes,
        "total_pendente": total_pendente,
        "total_vencido": total_vencido,
        "qtd_vencidas": qtd_vencidas,
        "qtd_lancamentos_mes": qtd_lancamentos_mes,
        "ultimos_lancamentos": ultimos_lancamentos,
    }


def atualizar_lancamento(lancamento, form):
    preencher_lancamento_com_form(
        lancamento=lancamento,
        form=form
    )

    db.session.commit()

    return lancamento

def marcar_lancamento_como_pago(lancamento):
    if lancamento.status == "pago":
        return False

    lancamento.status = "pago"
    lancamento.data_pagamento = date.today()

    db.session.commit()

    return True


def deletar_lancamento(lancamento):
    db.session.delete(lancamento)
    db.session.commit()


# CATEGORIAS
def criar_categoria_por_nome(nome, user_id):
    nome_normalizado = nome.strip().lower()

    if not nome_normalizado:
        raise ValueError("Informe o nome da categoria.")

    categoria_existente = CategoriaFinanceira.query.filter_by(
        nome=nome_normalizado,
        user_id=user_id
    ).first()

    if categoria_existente:
        raise ValueError("Você já possui uma categoria com esse nome.")

    categoria = CategoriaFinanceira(
        nome=nome_normalizado,
        user_id=user_id,
    )

    db.session.add(categoria)
    db.session.commit()

    return categoria


def criar_categoria(form, user_id):
    return criar_categoria_por_nome(
        nome=form.nome.data,
        user_id=user_id,
    )


def listar_categorias(user_id):
    return (
        CategoriaFinanceira.query.filter_by(user_id=user_id)
        .order_by(CategoriaFinanceira.nome.asc())
        .all()
    )


def atualizar_categoria(categoria, form):
    categoria.nome = form.nome.data.strip().lower()

    db.session.commit()

    return categoria


def deletar_categoria(categoria):
    if categoria.lancamentos:
        return False

    db.session.delete(categoria)
    db.session.commit()

    return True