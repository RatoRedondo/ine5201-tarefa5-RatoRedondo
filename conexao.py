import sqlite3
from pathlib import Path


ARQUIVO_BANCO = Path(__file__).with_name("estoque.db")
ARQUIVO_SQL = Path(__file__).with_name("banco.sql")


def criar_conexao(arquivo=ARQUIVO_BANCO):
    conexao = sqlite3.connect(str(arquivo))
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas(conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        sql = ARQUIVO_SQL.read_text(encoding="utf-8")
        conexao.executescript(sql)
        conexao.commit()
    finally:
        if fechar:
            conexao.close()
