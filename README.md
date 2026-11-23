# Sistema de Controle de Estoque

Sistema integrador desenvolvido em Python para a disciplina INE5201 -
Introdução à Ciência da Computação, da Universidade Federal de Santa Catarina.

## Funcionalidades

- cadastro, edição e exclusão de produtos;
- código único para cada produto;
- registro de entradas e saídas;
- atualização automática da quantidade após movimentações;
- consulta por nome ou código;
- filtro por categoria;
- histórico completo de movimentações;
- alertas para produtos com estoque menor ou igual ao mínimo;
- indicadores de quantidade de produtos, unidades e valor total;
- exportação dos resultados para CSV.
- autenticação de acesso com usuário e senha;
- backup manual e automático do banco SQLite;
- gráficos Matplotlib da quantidade em estoque;
- dashboard visual com indicadores e alertas.

## Diagrama do banco

```text
+----------------------+       +-----------------------------+
|       produtos       |       |       movimentacoes         |
+----------------------+       +-----------------------------+
| codigo PK            |<------| produto_codigo FK           |
| nome                 |       | id PK                       |
| categoria            |       | tipo ('entrada'/'saida')    |
| preco                |       | quantidade                  |
| quantidade           |       | data                        |
| estoque_minimo       |       +-----------------------------+
| data_cadastro        |
+----------------------+
```

O relacionamento é feito por `movimentacoes.produto_codigo` referenciando
`produtos.codigo`. Os scripts usam `PRAGMA foreign_keys = ON`.

## Requisitos

- Python 3.8 ou superior;
- `tkinter`, normalmente incluído na instalação padrão do Python.
- `matplotlib`.

Instale as dependências com:

```bash
python -m pip install -r requirements.txt
```

## Como executar

Na pasta do projeto:

```bash
python main.py
```

O acesso inicial usa `admin` como usuário e `admin123` como senha.
Um backup é criado automaticamente ao entrar no sistema e também pode ser
solicitado pelo botão **Fazer backup**.

Na primeira execução, `estoque.db` e suas tabelas são criados automaticamente
por `banco.sql`.

## Testes

```bash
python -m unittest test_sistema.py
```

Os testes cobrem cadastro, código repetido, entradas, saídas, limite de
estoque, indicadores e validações.

## Estrutura

| Arquivo | Descrição |
| --- | --- |
| `main.py` | Ponto de entrada da aplicação. |
| `estoque_gui.py` | Interface gráfica principal. |
| `conexao.py` | Conexão SQLite e inicialização do banco. |
| `produtos.py` | CRUD de produtos e consultas. |
| `movimentacoes.py` | Registro e histórico de movimentos. |
| `relatorios.py` | Indicadores e produtos com estoque baixo. |
| `validacoes.py` | Validações dos dados informados. |
| `exportacao.py` | Exportação de relatórios CSV. |
| `banco.sql` | Criação das tabelas e índices SQLite. |
| `test_sistema.py` | Testes automatizados. |
| `autenticacao.py` | Login e autenticação com senha protegida por hash. |
| `backup.py` | Backup automático e manual do banco. |
| `graficos.py` | Gráficos de quantidade em estoque com Matplotlib. |
| `requirements.txt` | Dependências do projeto. |

## Uso do GitHub Copilot

O GitHub Copilot foi utilizado como assistente para organizar o projeto em
módulos, estruturar as tabelas SQLite, implementar validações e movimentações,
preparar testes e elaborar esta documentação. Todas as sugestões foram revisadas
e executadas antes da entrega.
