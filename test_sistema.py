import unittest
from pathlib import Path
import tempfile

from autenticacao import autenticar, criar_usuario_padrao
from backup import criar_backup
from graficos import gerar_grafico_estoque
from conexao import criar_conexao, criar_tabelas
from movimentacoes import listar_movimentacoes, registrar_movimentacao
from produtos import buscar_produto, inserir_produto, listar_produtos
from relatorios import indicadores
from validacoes import validar_codigo, validar_preco, validar_quantidade


class SistemaEstoqueTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.conexao = criar_conexao(Path(self.temp.name) / "teste.db")
        criar_tabelas(self.conexao)

    def tearDown(self):
        self.conexao.close()
        self.temp.cleanup()

    def cadastrar(self, codigo="P001"):
        return inserir_produto({
            "codigo": codigo,
            "nome": "Notebook",
            "categoria": "Informática",
            "preco": "3500",
            "quantidade": "10",
            "estoque_minimo": "5",
        }, self.conexao)

    def test_cadastra_e_lista_produto(self):
        sucesso, _ = self.cadastrar()
        self.assertTrue(sucesso)
        self.assertEqual(buscar_produto("P001", self.conexao)["nome"], "Notebook")
        self.assertEqual(len(listar_produtos(self.conexao, categoria="Informática")), 1)

    def test_rejeita_codigo_repetido(self):
        self.cadastrar()
        sucesso, mensagem = self.cadastrar()
        self.assertFalse(sucesso)
        self.assertIn("código", mensagem.lower())

    def test_registra_entrada_e_saida(self):
        self.cadastrar()
        entrada, _ = registrar_movimentacao("P001", "entrada", 5, self.conexao)
        saida, _ = registrar_movimentacao("P001", "saida", 3, self.conexao)
        produto = buscar_produto("P001", self.conexao)
        self.assertTrue(entrada)
        self.assertTrue(saida)
        self.assertEqual(produto["quantidade"], 12)
        self.assertEqual(len(listar_movimentacoes(self.conexao)), 2)

    def test_impede_saida_acima_do_estoque(self):
        self.cadastrar()
        sucesso, _ = registrar_movimentacao("P001", "saida", 11, self.conexao)
        self.assertFalse(sucesso)

    def test_calcula_indicadores(self):
        self.cadastrar()
        dados = indicadores(self.conexao)
        self.assertEqual(dados["produtos"], 1)
        self.assertEqual(dados["unidades"], 10)
        self.assertEqual(dados["valor"], 35000)

    def test_valida_campos_numericos(self):
        self.assertTrue(validar_codigo("P-001"))
        self.assertFalse(validar_codigo("P 001"))
        self.assertTrue(validar_preco("12.50"))
        self.assertFalse(validar_preco("-1"))
        self.assertTrue(validar_quantidade("5"))
        self.assertFalse(validar_quantidade("-2"))

    def test_autenticacao_padrao(self):
        criar_usuario_padrao(self.conexao)
        self.assertTrue(autenticar("admin", "admin123", self.conexao))
        self.assertFalse(autenticar("admin", "senha-incorreta", self.conexao))

    def test_cria_backup(self):
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "estoque.db"
            banco.write_bytes(b"teste")
            destino = Path(pasta) / "backups"
            sucesso, caminho = criar_backup(banco, destino)
            self.assertTrue(sucesso)
            self.assertTrue(Path(caminho).exists())

    def test_gera_grafico_de_estoque(self):
        self.cadastrar()
        produtos = listar_produtos(self.conexao)
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "grafico.png"
            sucesso, _ = gerar_grafico_estoque(produtos, caminho)
            self.assertTrue(sucesso)
            self.assertTrue(caminho.exists())


if __name__ == "__main__":
    unittest.main()
