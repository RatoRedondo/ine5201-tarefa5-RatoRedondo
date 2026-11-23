import shutil
from datetime import datetime
from pathlib import Path

from conexao import ARQUIVO_BANCO


PASTA_BACKUP = Path(__file__).with_name("backups")


def criar_backup(arquivo_banco=ARQUIVO_BANCO, pasta_backup=PASTA_BACKUP):
    banco = Path(arquivo_banco)
    destino_pasta = Path(pasta_backup)
    if not banco.exists():
        return False, "Banco de dados ainda não existe."
    destino_pasta.mkdir(parents=True, exist_ok=True)
    nome = f"estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = destino_pasta / nome
    shutil.copy2(banco, destino)
    return True, str(destino)


def criar_backup_inicio(arquivo_banco=ARQUIVO_BANCO, pasta_backup=PASTA_BACKUP):
    return criar_backup(arquivo_banco, pasta_backup)
