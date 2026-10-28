"""Constantes do jogo: tela, cores, caminhos e níveis de dificuldade."""
from pathlib import Path

# Pasta raiz do projeto (um nível acima de src/).
RAIZ = Path(__file__).resolve().parent.parent
PASTA_SONS = RAIZ / "assets" / "sons"
ARQUIVO_RECORDE = RAIZ / "recorde.txt"

LARGURA, ALTURA = 960, 640
ALTURA_HUD = 48
TAMANHO = 32  # tamanho de um "bloco" do cenário e do robô
FPS = 60

TOTAL_ROBOS = 5
TOTAL_BATERIAS = 8

# Paleta única usada em todas as telas (menu, partida, pausa e fim).
PRETO = (8, 12, 28)
FUNDO = (13, 22, 48)
GRADE = (20, 34, 64)
AZUL_ESCURO = (22, 38, 72)
AZUL = (58, 145, 255)
CIANO = (95, 235, 255)
BRANCO = (239, 246, 255)
VERDE = (94, 239, 150)
AMARELO = (255, 218, 91)
VERMELHO = (255, 88, 105)
ROXO = (173, 115, 255)
CINZA = (110, 130, 160)
CINZA_ESCURO = (80, 85, 110)

# Cada dificuldade muda vidas, velocidade de queda da energia e dos perigos.
DIFICULDADES = [
    {"nome": "FÁCIL", "vidas": 4, "dreno_energia": 1.3, "velocidade_perigos": 0.8},
    {"nome": "NORMAL", "vidas": 3, "dreno_energia": 1.8, "velocidade_perigos": 1.0},
    {"nome": "DIFÍCIL", "vidas": 2, "dreno_energia": 2.4, "velocidade_perigos": 1.25},
]
DIFICULDADE_PADRAO = 1
