from flask import render_template, redirect, url_for, flash, request, Response, jsonify, current_app
from flask_login import login_required, current_user, logout_user
from io import StringIO
import csv
import smtplib

from app import db
from app.financeiro.notificacoes import enviar_alertas_vencimento
from app.financeiro import financeiro_bp
from app.models import LancamentoFinanceiro, CategoriaFinanceira
from app.financeiro.forms import LancamentoForm, CategoriaForm
from app.utils.formatters import padronizar_titulo
from app.financeiro.services import (
    obter_gastos_mensais_ano,
    criar_lancamento, obter_resumo_dashboard, listar_lancamentos_filtrados, atualizar_lancamento, marcar_lancamento_como_pago, deletar_lancamento,
    obter_agenda_financeira,
    obter_relatorio_mensal,
    criar_categoria, criar_categoria_por_nome, listar_categorias, atualizar_categoria, deletar_categoria
)



def carregar_categorias_no_form(form):
    categorias = listar_categorias(
        user_id=current_user.id
    )

    form.categoria.choices = [
        (0, "-- Selecione uma categoria --")
    ] + [
        (categoria.id, padronizar_titulo(categoria.nome))
        for categoria in categorias
    ]


# DASHBOARD
@financeiro_bp.route("/")
@login_required
def dashboard():
    resumo = obter_resumo_dashboard(user_id=current_user.id)

    grafico_mensal = obter_gastos_mensais_ano(user_id=current_user.id)

    return render_template("financeiro/dashboard.html", **resumo, grafico_mensal=grafico_mensal)


# AGENDA
@financeiro_bp.route("/agenda/")
@login_required
def agenda():
    dados_agenda = obter_agenda_financeira(
        user_id=current_user.id
    )

    return render_template(
        "financeiro/agenda.html",
        **dados_agenda,
    )


# ENVIAR AVISO EMAIl (P/ A APRESENTAÇÃO SÓ)
@financeiro_bp.route("/agenda/enviar-alertas/", methods=["POST"])
@login_required
def enviar_alertas_vencimento_view():
    try:
        resultado = enviar_alertas_vencimento(
            user_id=current_user.id
        )

    except (OSError, smtplib.SMTPException) as erro:
        current_app.logger.exception("Erro ao enviar alerta de vencimento por email.")

        flash(
            "Não foi possível enviar o email agora. Verifique a conexão com a internet e tente novamente.",
            "danger",
        )

        return redirect(
            url_for("financeiro.agenda")
        )

    emails_enviados = resultado["emails_enviados"]
    lancamentos_encontrados = resultado["lancamentos_encontrados"]

    if emails_enviados > 0:
        flash(
            f"Alerta enviado com sucesso: {lancamentos_encontrados} conta(s) vencem amanhã.",
            "success",
        )
    else:
        flash(
            "Nenhuma conta com vencimento para amanhã foi encontrada.",
            "info",
        )

    return redirect(
        url_for("financeiro.agenda")
    )


# CATEGORIA
@financeiro_bp.route("/categorias/")
@login_required
def listar_categorias_view():
    categorias = listar_categorias(
        user_id=current_user.id
    )

    return render_template(
        "financeiro/categorias.html",
        categorias=categorias,
    )

@financeiro_bp.route("/categorias/nova/", methods=["GET", "POST"])
@login_required
def nova_categoria():
    form = CategoriaForm()

    if form.validate_on_submit():
        try:
            criar_categoria(form, current_user.id)

            flash("Categoria criada com sucesso.", "success")
            return redirect(url_for("financeiro.listar_categorias_view"))

        except ValueError as erro:
            form.nome.errors.append(str(erro))

    return render_template("financeiro/categoria_form.html", form=form, titulo="Nova categoria",)

@financeiro_bp.route("/categorias/<int:id>/editar/", methods=["GET", "POST"])
@login_required
def editar_categoria(id):
    categoria = (
        CategoriaFinanceira.query
        .filter_by(
            id=id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    form = CategoriaForm(obj=categoria)

    if form.validate_on_submit():
        atualizar_categoria(
            categoria=categoria,
            form=form,
        )

        flash("Categoria atualizada com sucesso.", "success")

        return redirect(
            url_for("financeiro.listar_categorias_view")
        )

    return render_template(
        "financeiro/categoria_form.html",
        form=form,
        titulo="Editar categoria",
    )

@financeiro_bp.route("/categorias/<int:id>/deletar/", methods=["POST"])
@login_required
def deletar_categoria_view(id):
    categoria = (
        CategoriaFinanceira.query
        .filter_by(
            id=id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    deletou = deletar_categoria(categoria)

    if not deletou:
        flash(
            "Não é possível deletar esta categoria porque ela possui lançamentos vinculados.",
            "warning",
        )

        return redirect(
            url_for("financeiro.listar_categorias_view")
        )

    flash("Categoria deletada com sucesso.", "success")

    return redirect(
        url_for("financeiro.listar_categorias_view")
    )

# modal
@financeiro_bp.route("/categorias/criar-ajax/", methods=["POST"])
@login_required
def criar_categoria_ajax():
    nome = request.form.get("nome", "")

    try:
        categoria = criar_categoria_por_nome(
            nome=nome,
            user_id=current_user.id,
        )

        return jsonify({
            "ok": True,
            "id": categoria.id,
            "nome": padronizar_titulo(categoria.nome),
            "mensagem": "Categoria criada com sucesso.",
        })

    except ValueError as erro:
        return jsonify({
            "ok": False,
            "erro": str(erro),
        }), 400


# LANÇAMENTOS
@financeiro_bp.route("/lancamentos/")
@login_required
def listar_lancamentos():
    status = request.args.get("status")
    mes = request.args.get("mes")
    ano = request.args.get("ano")
    categoria_id = request.args.get("categoria_id")

    categorias = listar_categorias(user_id=current_user.id)

    lancamentos, total_somatorio = listar_lancamentos_filtrados(
        user_id=current_user.id,
        status=status,
        mes=mes,
        ano=ano,
        categoria_id=categoria_id,
    )

    tem_filtro = bool(status or ano or (categoria_id and categoria_id != "0"))

    return render_template(
        "financeiro/lancamentos.html",
        lancamentos=lancamentos,
        total_somatorio=total_somatorio,
        status_selecionado=status,
        mes_selecionado=mes,
        ano_selecionado=ano,
        categorias=categorias,
        tem_filtro=tem_filtro,
    )

@financeiro_bp.route("/lancamentos/novo/", methods=["GET", "POST"])
@login_required
def novo_lancamento():
    form = LancamentoForm()
    carregar_categorias_no_form(form)


    if form.validate_on_submit():
        criar_lancamento(
            form=form,
            user_id=current_user.id,
        )

        flash("Lançamento cadastrado com sucesso.", "success")

        return redirect(
            url_for("financeiro.listar_lancamentos")
        )
        

    return render_template(
        "financeiro/lancamento_form.html",
        form=form,
        titulo="Novo lançamento",
    )

@financeiro_bp.route("/lancamentos/<int:id>/pagar/", methods=["POST"])
@login_required
def pagar_lancamento(id):
    lancamento = (
        LancamentoFinanceiro.query
        .filter_by(
            id=id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    foi_pago = marcar_lancamento_como_pago(lancamento)

    if foi_pago:
        flash("Lançamento marcado como pago.", "success")
    else:
        flash("Este lançamento já está pago.", "info")

    return redirect(
        url_for("financeiro.listar_lancamentos")
    )

@financeiro_bp.route("/lancamentos/<int:id>/editar/", methods=["GET", "POST"])
@login_required
def editar_lancamento(id):
    lancamento = (
        LancamentoFinanceiro.query
        .filter_by(
            id=id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    form = LancamentoForm(obj=lancamento)
    carregar_categorias_no_form(form)

    if not form.is_submitted():
        form.categoria.data = lancamento.categoria_id or 0

    if form.validate_on_submit():
        atualizar_lancamento(
            lancamento=lancamento,
            form=form,
        )

        flash("Lançamento atualizado com sucesso.", "success")

        return redirect(
            url_for("financeiro.listar_lancamentos")
        )

    return render_template(
        "financeiro/lancamento_form.html",
        form=form,
        titulo="Editar lançamento",
    )

@financeiro_bp.route("/lancamentos/<int:id>/deletar/", methods=["POST"])
@login_required
def deletar_lancamento_view(id):
    lancamento = (
        LancamentoFinanceiro.query
        .filter_by(
            id=id,
            user_id=current_user.id,
        )
        .first_or_404()
    )

    deletar_lancamento(lancamento)

    flash("Lançamento removido com sucesso.", "success")

    return redirect(
        url_for("financeiro.listar_lancamentos")
    )

# RELATÓRIO
@financeiro_bp.route("/relatorio-mensal/")
@login_required
def relatorio_mensal():
    mes = request.args.get("mes")
    ano = request.args.get("ano")

    dados_relatorio = obter_relatorio_mensal(
        user_id=current_user.id,
        mes=mes,
        ano=ano,
    )

    return render_template(
        "financeiro/relatorio_mensal.html",
        **dados_relatorio,
    )

#EXPORTAR CSV 
def texto_csv(valor):
    if valor is None or valor == "":
        return "Não informado"

    return str(valor)


def data_csv(data):
    if not data:
        return "Não informado"

    return "'" + data.strftime("%d/%m/%Y")


def valor_csv(valor):
    if valor is None:
        return "R$ 0,00"

    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@financeiro_bp.route("/exportar-relatorio")
@login_required
def exportar_relatorio():
    output = StringIO()
    # output.write("sep=;\n")

    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "Categoria",
        "Favorecido",
        "Tipo de custo",
        "Conta de origem",
        "Forma de pagamento",
        "Status",
        "Valor",
        "Data de lançamento",
        "Data de vencimento",
        "Data de pagamento",
    ])

    transacoes = (
        LancamentoFinanceiro.query
        .filter_by(user_id=current_user.id)
        .order_by(LancamentoFinanceiro.data_lancamento.desc())
        .all()
    )

    for transacao in transacoes:
        categoria = (
            padronizar_titulo(transacao.categoria.nome)
            if transacao.categoria
            else "Sem categoria"
        )

        favorecido = (
            padronizar_titulo(transacao.favorecido)
            if transacao.favorecido
            else "Não informado"
        )

        tipo_custo = (
            padronizar_titulo(transacao.tipo_custo)
            if transacao.tipo_custo
            else "Não informado"
        )

        conta_origem = (
            padronizar_titulo(transacao.conta_origem)
            if transacao.conta_origem
            else "Não informado"
        )

        forma_pagamento = (
            padronizar_titulo(transacao.forma_pagamento)
            if transacao.forma_pagamento
            else "Não informado"
        )

        status = (
            padronizar_titulo(transacao.status)
            if transacao.status
            else "Não informado"
        )

        writer.writerow([
            categoria,
            favorecido,
            tipo_custo,
            conta_origem,
            forma_pagamento,
            status,
            valor_csv(transacao.valor),
            data_csv(transacao.data_lancamento),
            data_csv(transacao.data_vencimento),
            data_csv(transacao.data_pagamento),
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8-sig",
    )

    response.headers["Content-Disposition"] = "attachment; filename=relatorio.csv"

    return response


#PERFIL
@financeiro_bp.route('/atualizar_perfil', methods=['POST'])
@login_required
def atualizar_perfil():

    current_user.username = request.form.get('username')
    current_user.email = request.form.get('email')
    current_user.telefone = request.form.get('telefone')

    db.session.commit()

    flash('Perfil atualizado com sucesso!', 'success')

    return redirect(url_for('main.perfil'))

@financeiro_bp.route('/excluir_conta', methods=['POST'])
@login_required
def excluir_conta():

    usuario = current_user._get_current_object()

    db.session.delete(usuario)
    db.session.commit()

    logout_user()

    flash('Conta excluída com sucesso.', 'success')

    return redirect(url_for('auth.login'))