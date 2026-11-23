def gerar_grafico_estoque(produtos, caminho):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False, "Matplotlib não está instalado."

    if not produtos:
        return False, "Não há produtos para gerar o gráfico."

    nomes = [produto["nome"] for produto in produtos[:10]]
    quantidades = [produto["quantidade"] for produto in produtos[:10]]
    figura, eixo = plt.subplots(figsize=(9, 5))
    barras = eixo.bar(nomes, quantidades, color="#2471A3")
    eixo.set_title("Quantidade em estoque")
    eixo.set_xlabel("Produto")
    eixo.set_ylabel("Unidades")
    eixo.tick_params(axis="x", rotation=35)
    eixo.bar_label(barras)
    figura.tight_layout()
    figura.savefig(caminho, dpi=150)
    plt.close(figura)
    return True, str(caminho)
