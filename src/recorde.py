"""Leitura e gravação do recorde (maior pontuação) em arquivo texto."""
from .config import ARQUIVO_RECORDE


def carregar_recorde():
    try:
        return int(ARQUIVO_RECORDE.read_text(encoding="utf-8").strip() or 0)
    except (OSError, ValueError):
        # Arquivo ainda não existe ou foi corrompido: começa do zero.
        return 0


def salvar_recorde(pontos):
    try:
        ARQUIVO_RECORDE.write_text(str(pontos), encoding="utf-8")
    except OSError:
        pass  # sem permissão de escrita: o jogo segue sem salvar
