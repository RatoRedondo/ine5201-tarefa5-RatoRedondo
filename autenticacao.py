import hashlib
import sqlite3
import tkinter as tk
from tkinter import messagebox

from conexao import criar_conexao, criar_tabelas


def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def criar_usuario_padrao(conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabelas(conexao)
        existente = conexao.execute(
            "SELECT 1 FROM usuarios WHERE usuario=?",
            ("admin",),
        ).fetchone()
        if not existente:
            conexao.execute(
                "INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
                ("admin", hash_senha("admin123")),
            )
            conexao.commit()
        return True
    finally:
        if fechar:
            conexao.close()


def autenticar(usuario, senha, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_usuario_padrao(conexao)
        linha = conexao.execute(
            "SELECT senha_hash FROM usuarios WHERE usuario=?",
            (usuario.strip(),),
        ).fetchone()
        return bool(linha and linha["senha_hash"] == hash_senha(senha))
    finally:
        if fechar:
            conexao.close()


def solicitar_login(root, conexao=None):
    resultado = {"autorizado": False}
    janela = tk.Toplevel(root)
    janela.title("Acesso ao sistema")
    janela.geometry("340x170")
    janela.resizable(False, False)
    janela.grab_set()

    usuario = tk.StringVar()
    senha = tk.StringVar()
    tk.Label(janela, text="Usuário:", width=12, anchor="w").grid(
        row=0, column=0, padx=12, pady=(24, 6)
    )
    entrada_usuario = tk.Entry(janela, textvariable=usuario)
    entrada_usuario.grid(row=0, column=1, padx=12, pady=(24, 6))
    tk.Label(janela, text="Senha:", width=12, anchor="w").grid(
        row=1, column=0, padx=12, pady=6
    )
    entrada_senha = tk.Entry(janela, textvariable=senha, show="*")
    entrada_senha.grid(row=1, column=1, padx=12, pady=6)

    def tentar():
        if autenticar(usuario.get(), senha.get(), conexao):
            resultado["autorizado"] = True
            janela.destroy()
        else:
            messagebox.showerror(
                "Acesso negado",
                "Usuário ou senha incorretos.",
                parent=janela,
            )
            entrada_senha.delete(0, tk.END)

    tk.Button(janela, text="Entrar", command=tentar, width=12).grid(
        row=2, column=1, sticky="w", padx=12, pady=18
    )
    entrada_usuario.focus_set()
    janela.bind("<Return>", lambda event: tentar())
    root.wait_window(janela)
    return resultado["autorizado"]
