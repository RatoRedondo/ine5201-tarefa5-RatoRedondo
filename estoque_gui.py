import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from backup import criar_backup
from conexao import criar_conexao, criar_tabelas
from exportacao import exportar_csv
from graficos import gerar_grafico_estoque
from movimentacoes import listar_movimentacoes, registrar_movimentacao
from produtos import (
    atualizar_produto,
    excluir_produto,
    inserir_produto,
    listar_categorias,
    listar_produtos,
)
from relatorios import indicadores, produtos_estoque_baixo
from validacoes import (
    validar_codigo,
    validar_movimentacao,
    validar_preco,
    validar_quantidade,
    validar_texto,
)


class SistemaEstoque:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Estoque")
        self.root.geometry("980x620")
        self.root.minsize(900, 560)
        self.conexao = criar_conexao()
        criar_tabelas(self.conexao)
        self.status = tk.StringVar(value="Sistema pronto.")
        self.criar_layout()
        self.atualizar_produtos()
        self.atualizar_relatorios()

    def criar_layout(self):
        tk.Label(
            self.root,
            text="CONTROLE DE ESTOQUE",
            font=("Arial", 20, "bold"),
            fg="#17324D",
            pady=8,
        ).pack(fill=tk.X)

        abas = ttk.Notebook(self.root)
        abas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        aba_produtos = ttk.Frame(abas)
        aba_movimentos = ttk.Frame(abas)
        aba_relatorios = ttk.Frame(abas)
        abas.add(aba_produtos, text="Produtos")
        abas.add(aba_movimentos, text="Movimentações")
        abas.add(aba_relatorios, text="Relatórios")

        self.criar_aba_produtos(aba_produtos)
        self.criar_aba_movimentacoes(aba_movimentos)
        self.criar_aba_relatorios(aba_relatorios)
        tk.Label(
            self.root,
            textvariable=self.status,
            anchor="w",
            relief=tk.SUNKEN,
            padx=8,
        ).pack(fill=tk.X, side=tk.BOTTOM)

    def criar_aba_produtos(self, pai):
        formulario = tk.LabelFrame(pai, text="Cadastro de produtos", padx=10, pady=8)
        formulario.pack(fill=tk.X, padx=8, pady=8)
        self.codigo = tk.StringVar()
        self.nome = tk.StringVar()
        self.categoria = tk.StringVar()
        self.preco = tk.StringVar()
        self.quantidade = tk.StringVar(value="0")
        self.estoque_minimo = tk.StringVar(value="5")
        campos = (
            ("Código:", self.codigo),
            ("Nome:", self.nome),
            ("Categoria:", self.categoria),
            ("Preço:", self.preco),
            ("Quantidade:", self.quantidade),
            ("Estoque mínimo:", self.estoque_minimo),
        )
        for indice, (rotulo, variavel) in enumerate(campos):
            linha = indice // 2
            coluna = (indice % 2) * 2
            tk.Label(formulario, text=rotulo, width=14, anchor="w").grid(
                row=linha, column=coluna, padx=4, pady=4, sticky="w"
            )
            tk.Entry(formulario, textvariable=variavel, width=24).grid(
                row=linha, column=coluna + 1, padx=4, pady=4
            )

        botoes = tk.Frame(formulario)
        botoes.grid(row=0, column=4, rowspan=3, padx=20)
        for indice, (texto, comando) in enumerate((
            ("Cadastrar", self.cadastrar),
            ("Editar", self.editar),
            ("Excluir", self.excluir),
            ("Limpar", self.limpar),
        )):
            tk.Button(botoes, text=texto, command=comando, width=12).grid(
                row=indice, column=0, pady=2
            )

        filtros = tk.Frame(pai)
        filtros.pack(fill=tk.X, padx=8)
        self.busca = tk.StringVar()
        self.filtro_categoria = tk.StringVar(value="")
        tk.Label(filtros, text="Buscar:").pack(side=tk.LEFT)
        tk.Entry(filtros, textvariable=self.busca, width=28).pack(side=tk.LEFT, padx=5)
        tk.Label(filtros, text="Categoria:").pack(side=tk.LEFT)
        self.combo_categoria = ttk.Combobox(
            filtros, textvariable=self.filtro_categoria, width=20
        )
        self.combo_categoria.pack(side=tk.LEFT, padx=5)
        tk.Button(filtros, text="Consultar", command=self.atualizar_produtos).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(filtros, text="Exportar CSV", command=self.exportar).pack(
            side=tk.RIGHT
        )
        tk.Button(filtros, text="Fazer backup", command=self.fazer_backup).pack(
            side=tk.RIGHT, padx=5
        )

        tabela_frame = tk.Frame(pai)
        tabela_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        colunas = ("codigo", "nome", "categoria", "preco", "quantidade", "estoque_minimo")
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings")
        textos = (
            ("codigo", "Código", 100),
            ("nome", "Nome", 180),
            ("categoria", "Categoria", 140),
            ("preco", "Preço", 90),
            ("quantidade", "Quantidade", 100),
            ("estoque_minimo", "Mínimo", 90),
        )
        for coluna, texto, largura in textos:
            self.tabela.heading(coluna, text=texto)
            self.tabela.column(coluna, width=largura)
        barra = ttk.Scrollbar(tabela_frame, orient=tk.VERTICAL, command=self.tabela.yview)
        barra_h = ttk.Scrollbar(tabela_frame, orient=tk.HORIZONTAL, command=self.tabela.xview)
        self.tabela.configure(yscrollcommand=barra.set, xscrollcommand=barra_h.set)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")
        tabela_frame.rowconfigure(0, weight=1)
        tabela_frame.columnconfigure(0, weight=1)
        self.tabela.bind("<<TreeviewSelect>>", self.selecionar)

    def criar_aba_movimentacoes(self, pai):
        painel = tk.LabelFrame(pai, text="Nova movimentação", padx=12, pady=12)
        painel.pack(fill=tk.X, padx=10, pady=10)
        self.mov_codigo = tk.StringVar()
        self.mov_tipo = tk.StringVar(value="entrada")
        self.mov_quantidade = tk.StringVar()
        tk.Label(painel, text="Código do produto:").grid(row=0, column=0, sticky="w")
        tk.Entry(painel, textvariable=self.mov_codigo, width=25).grid(row=0, column=1, padx=5)
        tk.Label(painel, text="Tipo:").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Combobox(
            painel,
            textvariable=self.mov_tipo,
            values=("entrada", "saida"),
            state="readonly",
            width=22,
        ).grid(row=1, column=1, padx=5)
        tk.Label(painel, text="Quantidade:").grid(row=2, column=0, sticky="w")
        tk.Entry(painel, textvariable=self.mov_quantidade, width=25).grid(row=2, column=1, padx=5)
        tk.Button(painel, text="Registrar", command=self.registrar, width=15).grid(
            row=3, column=1, pady=12, sticky="w"
        )

        tk.Label(pai, text="Histórico", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        frame = tk.Frame(pai)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        colunas = ("id", "produto_codigo", "nome", "tipo", "quantidade", "data")
        self.historico = ttk.Treeview(frame, columns=colunas, show="headings")
        for coluna, texto, largura in (
            ("id", "ID", 50),
            ("produto_codigo", "Código", 100),
            ("nome", "Produto", 180),
            ("tipo", "Tipo", 90),
            ("quantidade", "Quantidade", 100),
            ("data", "Data", 150),
        ):
            self.historico.heading(coluna, text=texto)
            self.historico.column(coluna, width=largura)
        self.historico.pack(fill=tk.BOTH, expand=True)
        self.atualizar_historico()

    def criar_aba_relatorios(self, pai):
        self.indicadores = {}
        grade = tk.Frame(pai)
        grade.pack(fill=tk.X, padx=10, pady=12)
        for coluna, chave in enumerate(("produtos", "unidades", "valor", "estoque_baixo")):
            var = tk.StringVar(value="0")
            self.indicadores[chave] = var
            caixa = tk.LabelFrame(grade, padx=12, pady=12)
            caixa.grid(row=0, column=coluna, padx=6, sticky="ew")
            grade.columnconfigure(coluna, weight=1)
            tk.Label(caixa, textvariable=var, font=("Arial", 18, "bold")).pack()
            tk.Label(caixa, text=chave.replace("_", " ").title()).pack()

        tk.Button(
            pai,
            text="Gerar gráfico de estoque",
            command=self.gerar_grafico,
            width=22,
        ).pack(anchor="e", padx=10)

        tk.Label(pai, text="Produtos com estoque baixo", font=("Arial", 12, "bold")).pack(
            anchor="w", padx=10
        )
        frame = tk.Frame(pai)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.baixo = ttk.Treeview(
            frame,
            columns=("codigo", "nome", "quantidade", "estoque_minimo"),
            show="headings",
        )
        for coluna, texto in (
            ("codigo", "Código"),
            ("nome", "Produto"),
            ("quantidade", "Quantidade"),
            ("estoque_minimo", "Estoque mínimo"),
        ):
            self.baixo.heading(coluna, text=texto)
            self.baixo.column(coluna, width=180)
        self.baixo.pack(fill=tk.BOTH, expand=True)

    def dados_produto(self):
        return {
            "codigo": self.codigo.get(),
            "nome": self.nome.get(),
            "categoria": self.categoria.get(),
            "preco": self.preco.get(),
            "quantidade": self.quantidade.get(),
            "estoque_minimo": self.estoque_minimo.get(),
        }

    def validar_produto(self, dados):
        if not validar_codigo(dados["codigo"]):
            return "Informe um código válido."
        if not validar_texto(dados["nome"]):
            return "Informe o nome do produto."
        if not validar_preco(dados["preco"]):
            return "Informe um preço válido."
        if not validar_quantidade(dados["quantidade"]):
            return "Quantidade não pode ser negativa."
        if not validar_quantidade(dados["estoque_minimo"]):
            return "Estoque mínimo não pode ser negativo."
        return None

    def cadastrar(self):
        dados = self.dados_produto()
        erro = self.validar_produto(dados)
        if erro:
            messagebox.showwarning("Validação", erro)
            self.status.set(erro)
            return
        sucesso, mensagem = inserir_produto(dados, self.conexao)
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Cadastro", mensagem)
            self.limpar()
        else:
            messagebox.showerror("Erro", mensagem)

    def editar(self):
        dados = self.dados_produto()
        erro = self.validar_produto(dados)
        if erro:
            messagebox.showwarning("Validação", erro)
            return
        sucesso, mensagem = atualizar_produto(dados, self.conexao)
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Edição", mensagem)
            self.atualizar_produtos()
            self.limpar()
        else:
            messagebox.showerror("Erro", mensagem)

    def excluir(self):
        codigo = self.codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Validação", "Selecione um produto.")
            return
        if not messagebox.askyesno("Confirmar exclusão", f"Excluir o produto {codigo}?"):
            return
        sucesso, mensagem = excluir_produto(codigo, self.conexao)
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Exclusão", mensagem)
            self.limpar()
        else:
            messagebox.showerror("Erro", mensagem)

    def registrar(self):
        codigo = self.mov_codigo.get().strip()
        tipo = self.mov_tipo.get()
        quantidade = self.mov_quantidade.get()
        if not codigo:
            messagebox.showwarning("Validação", "Informe o código do produto.")
            return
        if not validar_movimentacao(quantidade):
            messagebox.showwarning("Validação", "Quantidade deve ser maior que zero.")
            return
        sucesso, mensagem = registrar_movimentacao(
            codigo, tipo, quantidade, self.conexao
        )
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Movimentação", mensagem)
            self.mov_codigo.set("")
            self.mov_quantidade.set("")
            self.atualizar_produtos()
            self.atualizar_historico()
            self.atualizar_relatorios()
        else:
            messagebox.showerror("Erro", mensagem)

    def selecionar(self, event=None):
        selecionado = self.tabela.selection()
        if not selecionado:
            return
        valores = self.tabela.item(selecionado[0], "values")
        self.codigo.set(valores[0])
        self.nome.set(valores[1])
        self.categoria.set(valores[2])
        self.preco.set(valores[3])
        self.quantidade.set(valores[4])
        self.estoque_minimo.set(valores[5])
        self.status.set(f"Produto {valores[0]} selecionado.")

    def atualizar_produtos(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        produtos = listar_produtos(
            self.conexao,
            self.busca.get(),
            self.filtro_categoria.get(),
        )
        for produto in produtos:
            self.tabela.insert("", tk.END, values=(
                produto["codigo"],
                produto["nome"],
                produto["categoria"] or "",
                f'{produto["preco"]:.2f}',
                produto["quantidade"],
                produto["estoque_minimo"],
            ))
        categorias = listar_categorias(self.conexao)
        self.combo_categoria.configure(values=("", *categorias))
        self.status.set(f"{len(produtos)} produto(s) encontrado(s).")
        self.atualizar_relatorios()

    def atualizar_historico(self):
        for item in self.historico.get_children():
            self.historico.delete(item)
        for movimento in listar_movimentacoes(self.conexao):
            self.historico.insert("", tk.END, values=(
                movimento["id"],
                movimento["produto_codigo"],
                movimento["nome"],
                movimento["tipo"],
                movimento["quantidade"],
                movimento["data"],
            ))

    def atualizar_relatorios(self):
        dados = indicadores(self.conexao)
        self.indicadores["produtos"].set(str(dados["produtos"]))
        self.indicadores["unidades"].set(str(dados["unidades"]))
        self.indicadores["valor"].set(f'R$ {dados["valor"]:.2f}')
        self.indicadores["estoque_baixo"].set(str(dados["estoque_baixo"]))
        for item in self.baixo.get_children():
            self.baixo.delete(item)
        for produto in produtos_estoque_baixo(self.conexao):
            self.baixo.insert("", tk.END, values=(
                produto["codigo"],
                produto["nome"],
                produto["quantidade"],
                produto["estoque_minimo"],
            ))

    def fazer_backup(self):
        sucesso, destino = criar_backup()
        if sucesso:
            messagebox.showinfo("Backup", f"Backup criado em:\n{destino}")
            self.status.set("Backup realizado com sucesso.")
        else:
            messagebox.showerror("Backup", destino)

    def gerar_grafico(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png")],
            initialfile="grafico_estoque.png",
        )
        if not caminho:
            return
        produtos = listar_produtos(self.conexao)
        sucesso, mensagem = gerar_grafico_estoque(produtos, caminho)
        if sucesso:
            messagebox.showinfo("Gráfico", f"Gráfico salvo em:\n{mensagem}")
        else:
            messagebox.showerror("Gráfico", mensagem)

    def exportar(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
            initialfile="estoque.csv",
        )
        if not caminho:
            return
        produtos = listar_produtos(
            self.conexao,
            self.busca.get(),
            self.filtro_categoria.get(),
        )
        try:
            exportar_csv(caminho, produtos)
            messagebox.showinfo("Exportação", "Relatório exportado com sucesso.")
        except OSError as erro:
            messagebox.showerror("Erro", f"Não foi possível exportar: {erro}")

    def limpar(self):
        for variavel in (
            self.codigo,
            self.nome,
            self.categoria,
            self.preco,
            self.busca,
        ):
            variavel.set("")
        self.quantidade.set("0")
        self.estoque_minimo.set("5")
        self.status.set("Formulário limpo.")
        self.atualizar_produtos()

    def fechar(self):
        self.conexao.close()
        self.root.destroy()


def main(root=None):
    root = root or tk.Tk()
    app = SistemaEstoque(root)
    root.protocol("WM_DELETE_WINDOW", app.fechar)
    root.mainloop()


if __name__ == "__main__":
    main()
