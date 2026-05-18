# arquivo p/ guardar funções de formatação
    # p/ deixar valores mais bonitos na tela :P

def padronizar_titulo(valor):
    if not valor:
        return ""
    return str(valor).strip().title()

def moeda(valor):
    if valor is None:
        return "R$ 0,00"

    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


def data_br(data):
    if not data:
        return "-"

    return data.strftime("%d/%m/%Y")


def status_label(status):
    labels = {
        "pendente": "Pendente",
        "pago": "Pago",
    }

    return labels.get(status, status)


def tipo_custo_label(tipo_custo):
    labels = {
        "fixo": "Fixo",
        "variavel": "Variável",
    }

    return labels.get(tipo_custo, tipo_custo)


# Para puxar apenas essa função no app/__init__ ao invés de uma por uma
def registrar_filtros(app):
    app.jinja_env.filters["padronizar_titulo"] = padronizar_titulo
    app.jinja_env.filters["moeda"] = moeda
    app.jinja_env.filters["data_br"] = data_br
    app.jinja_env.filters["status_label"] = status_label
    app.jinja_env.filters["tipo_custo_label"] = tipo_custo_label