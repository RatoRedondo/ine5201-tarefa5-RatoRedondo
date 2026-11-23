import sqlite3
from conexao import criar_conexao, criar_tabelas


def inserir_produto(dados, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabelas(conexao)
        conexao.execute(
            "INSERT INTO produtos (codigo, nome, categoria, preco, quantidade, estoque_minimo) VALUES (?, ?, ?, ?, ?, ?)",
            (
                dados["codigo"].strip(),
                dados["nome"].strip(),
                dados["categoria"].strip(),
                float(dados["preco"]),
                int(dados.get("quantidade", 0)),
                int(dados.get("estoque_minimo", 5)),
            ),
        )
        conexao.commit()
        return True, "Produto cadastrado com sucesso."
    except sqlite3.IntegrityError:
        return False, "Já existe um produto com esse código."
    except sqlite3.Error as erro:
        return False, f"Erro ao cadastrar produto: {erro}"
    finally:
        if fechar:
            conexao.close()


def atualizar_produto(dados, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabelas(conexao)
        cursor = conexao.execute(
            "UPDATE produtos SET nome=?, categoria=?, preco=?, estoque_minimo=? WHERE codigo=?",
            (
                dados["nome"].strip(),
                dados["categoria"].strip(),
                float(dados["preco"]),
                int(dados.get("estoque_minimo", 5)),
                dados["codigo"].strip(),
            ),
        )
        conexao.commit()
        if cursor.rowcount:
            return True, "Produto atualizado com sucesso."
        return False, "Produto não encontrado."
    finally:
        if fechar:
            conexao.close()


def excluir_produto(codigo, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        cursor = conexao.execute("DELETE FROM produtos WHERE codigo=?", (codigo.strip(),))
        conexao.commit()
        if cursor.rowcount:
            return True, "Produto excluído com sucesso."
        return False, "Produto não encontrado."
    except sqlite3.IntegrityError:
        return False, "Não é possível excluir: existem movimentações relacionadas."
    finally:
        if fechar:
            conexao.close()


def buscar_produto(codigo, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        linha = conexao.execute(
            "SELECT * FROM produtos WHERE codigo=?", (codigo.strip(),)
        ).fetchone()
        return dict(linha) if linha else None
    finally:
        if fechar:
            conexao.close()


def listar_produtos(conexao=None, termo="", categoria=""):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        filtros = []
        parametros = []
        if termo.strip():
            filtros.append("(LOWER(codigo) LIKE ? OR LOWER(nome) LIKE ?)")
            filtro = f"%{termo.lower()}%"
            parametros.extend((filtro, filtro))
        if categoria.strip():
            filtros.append("categoria=?")
            parametros.append(categoria.strip())
        consulta = "SELECT * FROM produtos"
        if filtros:
            consulta += " WHERE " + " AND ".join(filtros)
        consulta += " ORDER BY nome"
        linhas = conexao.execute(consulta, parametros).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        if fechar:
            conexao.close()


def listar_categorias(conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        linhas = conexao.execute(
            "SELECT DISTINCT categoria FROM produtos WHERE TRIM(COALESCE(categoria, '')) != '' ORDER BY categoria"
        ).fetchall()
        return [linha["categoria"] for linha in linhas]
    finally:
        if fechar:
            conexao.close()
