import csv


def exportar_csv(caminho, linhas):
    with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(("Código", "Nome", "Categoria", "Preço", "Quantidade", "Estoque mínimo"))
        for produto in linhas:
            escritor.writerow((
                produto["codigo"],
                produto["nome"],
                produto["categoria"] or "",
                f'{produto["preco"]:.2f}',
                produto["quantidade"],
                produto["estoque_minimo"],
            ))
