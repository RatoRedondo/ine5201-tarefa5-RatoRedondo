import tkinter as tk

from autenticacao import solicitar_login
from backup import criar_backup_inicio
from conexao import criar_conexao, criar_tabelas
from estoque_gui import main as abrir_sistema


def main():
    root = tk.Tk()
    root.withdraw()
    conexao = criar_conexao()
    criar_tabelas(conexao)
    if not solicitar_login(root, conexao):
        conexao.close()
        root.destroy()
        return
    conexao.close()
    criar_backup_inicio()
    root.deiconify()
    abrir_sistema(root)


if __name__ == "__main__":
    main()
