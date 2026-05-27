from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user, logout_user

import csv
from io import StringIO

from app import db

from app.financeiro import financeiro_bp
from app.models import LancamentoFinanceiro, CategoriaFinanceira
from app.financeiro.forms import LancamentoForm, CategoriaForm
from app.utils.formatters import padronizar_titulo
from app.financeiro.services import (
    obter_gastos_mensais_ano,
    criar_lancamento, obter_resumo_dashboard, listar_lancamentos_filtrados, atualizar_lancamento, marcar_lancamento_como_pago, deletar_lancamento,
    obter_agenda_financeira,
    obter_relatorio_mensal,
    criar_categoria, listar_categorias, atualizar_categoria, deletar_categoria
)



def carregar_categorias_no_form(form):
    categorias = listar_categorias(
        user_id=current_user.id
    )

    form.categoria.choices = [
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


# LANÇAMENTOS
@financeiro_bp.route("/lancamentos/")
@login_required
def listar_lancamentos():
    status = request.args.get("status")
    mes = request.args.get("mes")
    ano = request.args.get("ano")
    categoria_id = request.args.get("categoria_id")

    categorias = listar_categorias(user_id=current_user.id)

    lancamentos, total_filtrado = listar_lancamentos_filtrados(
        user_id=current_user.id,
        status=status,
        mes=mes,
        ano=ano,
        categoria_id=categoria_id,
    )

    return render_template(
        "financeiro/lancamentos.html",
        lancamentos=lancamentos,
        total_filtrado=total_filtrado,
        status_selecionado=status,
        mes_selecionado=mes,
        ano_selecionado=ano,
        categorias=categorias,
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

@financeiro_bp.route('/exportar-relatorio')
@login_required
def exportar_relatorio():

    output = StringIO()
    writer = csv.writer(output, delimiter=';')

    # Cabeçalho
    writer.writerow([
        "Categoria",
        "Fornecedor",
        "Despesa",
        "Origem",
        "Pagamento",
        "Status",
        "Valor",
        "Data",
    ])

    transacoes = LancamentoFinanceiro.query.filter_by(
        user_id=current_user.id
    ).all()

    # Dados do banco
    for transacao in transacoes:
        writer.writerow([
            transacao.categoria.nome,
            transacao.favorecido,
            transacao.tipo_custo,
            transacao.conta_origem,
            transacao.forma_pagamento,
            transacao.status,
            transacao.valor,
            transacao.data_lancamento,
        ])

    response = Response(
        output.getvalue(),
        mimetype='text/csv'
    )

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=relatorio.csv"

    return response

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