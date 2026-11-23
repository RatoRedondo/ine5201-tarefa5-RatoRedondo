import re


def validar_codigo(codigo):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", codigo.strip()))


def validar_texto(texto):
    return bool(texto and texto.strip())


def validar_preco(preco):
    try:
        return float(preco) >= 0
    except (TypeError, ValueError):
        return False


def validar_quantidade(quantidade):
    try:
        valor = int(quantidade)
        return valor >= 0
    except (TypeError, ValueError):
        return False


def validar_movimentacao(quantidade):
    try:
        return int(quantidade) > 0
    except (TypeError, ValueError):
        return False
