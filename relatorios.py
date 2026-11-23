from conexao import criar_conexao


def indicadores(conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        totais = conexao.execute(
            """
            SELECT COUNT(*) AS produtos,
                   COALESCE(SUM(quantidade), 0) AS unidades,
                   COALESCE(SUM(preco * quantidade), 0) AS valor
            FROM produtos
            """
        ).fetchone()
        baixo = conexao.execute(
            "SELECT COUNT(*) AS quantidade FROM produtos WHERE quantidade <= estoque_minimo"
        ).fetchone()
        return {
            "produtos": totais["produtos"],
            "unidades": totais["unidades"],
            "valor": float(totais["valor"]),
            "estoque_baixo": baixo["quantidade"],
        }
    finally:
        if fechar:
            conexao.close()


def produtos_estoque_baixo(conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        linhas = conexao.execute(
            "SELECT * FROM produtos WHERE quantidade <= estoque_minimo ORDER BY quantidade"
        ).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        if fechar:
            conexao.close()
