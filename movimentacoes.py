import sqlite3
from conexao import criar_conexao


def registrar_movimentacao(produto_codigo, tipo, quantidade, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            return False, "Quantidade deve ser maior que zero."
        if tipo not in ("entrada", "saida"):
            return False, "Tipo de movimentação inválido."

        produto = conexao.execute(
            "SELECT quantidade FROM produtos WHERE codigo=?",
            (produto_codigo,),
        ).fetchone()
        if not produto:
            return False, "Produto não encontrado."

        nova_quantidade = (
            produto["quantidade"] + quantidade
            if tipo == "entrada"
            else produto["quantidade"] - quantidade
        )
        if nova_quantidade < 0:
            return False, "Saída maior que o estoque disponível."

        conexao.execute(
            "INSERT INTO movimentacoes (produto_codigo, tipo, quantidade) VALUES (?, ?, ?)",
            (produto_codigo, tipo, quantidade),
        )
        conexao.execute(
            "UPDATE produtos SET quantidade=? WHERE codigo=?",
            (nova_quantidade, produto_codigo),
        )
        conexao.commit()
        return True, "Movimentação registrada com sucesso."
    except sqlite3.Error as erro:
        conexao.rollback()
        return False, f"Erro ao registrar movimentação: {erro}"
    finally:
        if fechar:
            conexao.close()


def listar_movimentacoes(conexao=None, produto_codigo=""):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        if produto_codigo.strip():
            linhas = conexao.execute(
                """
                SELECT m.*, p.nome
                FROM movimentacoes m
                JOIN produtos p ON p.codigo=m.produto_codigo
                WHERE m.produto_codigo=? ORDER BY m.data DESC, m.id DESC
                """,
                (produto_codigo.strip(),),
            ).fetchall()
        else:
            linhas = conexao.execute(
                """
                SELECT m.*, p.nome
                FROM movimentacoes m
                JOIN produtos p ON p.codigo=m.produto_codigo
                ORDER BY m.data DESC, m.id DESC
                """
            ).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        if fechar:
            conexao.close()
