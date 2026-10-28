"""Gera as duas trilhas de fundo do jogo (menu e partida) em WAV.

As músicas são sintetizadas aqui mesmo, com ondas simples (quadrada e
triangular) no estilo chiptune. Assim o jogo não depende de áudio de
terceiros e não há licença a creditar.

Uso (na pasta do projeto):
    python tools/gerar_musicas.py
"""
import array
import math
import wave
from pathlib import Path

TAXA = 22050  # amostras por segundo
PASTA_SONS = Path(__file__).resolve().parent.parent / "assets" / "sons"

# Frequência de uma nota a partir do número MIDI (69 = Lá 440 Hz).
def freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def onda_quadrada(fase, ciclo=0.5):
    return 1.0 if (fase % 1.0) < ciclo else -1.0


def onda_triangular(fase):
    f = fase % 1.0
    return 4 * f - 1 if f < 0.5 else 3 - 4 * f


def envelope(t, duracao, ataque=0.01, soltura=0.08):
    """Sobe rápido no início e cai no fim da nota, evitando estalos."""
    if t < ataque:
        return t / ataque
    if t > duracao - soltura:
        return max(0.0, (duracao - t) / soltura)
    return 1.0


def adicionar_nota(buffer, inicio, duracao, midi, volume, tipo="quadrada", ciclo=0.5):
    """Soma uma nota ao buffer (lista de floats) a partir do segundo `inicio`."""
    f = freq(midi)
    i0 = int(inicio * TAXA)
    n = int(duracao * TAXA)
    for i in range(n):
        if i0 + i >= len(buffer):
            break
        t = i / TAXA
        fase = f * t
        if tipo == "quadrada":
            valor = onda_quadrada(fase, ciclo)
        else:
            valor = onda_triangular(fase)
        buffer[i0 + i] += valor * volume * envelope(t, duracao)


def salvar(buffer, nome, pico=0.2):
    """Normaliza o volume e grava WAV mono 16 bits."""
    maior = max(abs(v) for v in buffer) or 1.0
    escala = pico * 32767 / maior
    dados = array.array("h", (int(v * escala) for v in buffer))
    with wave.open(str(PASTA_SONS / nome), "wb") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(TAXA)
        arquivo.writeframes(dados.tobytes())
    print(f"Gerado: {nome} ({len(buffer) / TAXA:.1f} s)")


# Acordes (notas MIDI): Lá menor, Fá maior, Dó maior, Sol maior / Mi menor.
AM, F, C, G, EM = [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [52, 55, 59]


def musica_menu():
    """Clima misterioso e lento: estação vazia, esperando a missão."""
    bpm = 80
    tempo_batida = 60 / bpm
    acordes = [AM, F, C, G]
    batidas_por_acorde = 8
    total = len(acordes) * batidas_por_acorde * tempo_batida
    buffer = [0.0] * int(total * TAXA)
    for indice, acorde in enumerate(acordes):
        inicio_acorde = indice * batidas_por_acorde * tempo_batida
        # Fundo (pad) triangular sustentando o acorde inteiro.
        for nota in acorde:
            adicionar_nota(buffer, inicio_acorde, batidas_por_acorde * tempo_batida, nota - 12,
                           0.18, "triangular")
        # Arpejo lento em colcheias, uma oitava acima.
        padrao = [0, 1, 2, 1, 0, 2, 1, 2]
        for passo in range(batidas_por_acorde * 2):
            nota = acorde[padrao[passo % len(padrao)]] + 12
            adicionar_nota(buffer, inicio_acorde + passo * tempo_batida / 2,
                           tempo_batida / 2 * 0.9, nota, 0.10, "quadrada", 0.25)
    salvar(buffer, "musica_menu.wav", pico=0.20)


def musica_partida():
    """Ritmo mais rápido e tenso: a energia está acabando."""
    bpm = 128
    tempo_batida = 60 / bpm
    acordes = [AM, F, G, EM]
    batidas_por_acorde = 8
    total = len(acordes) * batidas_por_acorde * tempo_batida
    buffer = [0.0] * int(total * TAXA)
    for indice, acorde in enumerate(acordes):
        inicio_acorde = indice * batidas_por_acorde * tempo_batida
        raiz = acorde[0] - 24
        # Baixo pulsando em colcheias (raiz e oitava alternadas).
        for passo in range(batidas_por_acorde * 2):
            nota = raiz if passo % 2 == 0 else raiz + 12
            adicionar_nota(buffer, inicio_acorde + passo * tempo_batida / 2,
                           tempo_batida / 2 * 0.8, nota, 0.22, "triangular")
        # Arpejo rápido em semicolcheias.
        padrao = [0, 1, 2, 3]
        notas = acorde + [acorde[0] + 12]
        for passo in range(batidas_por_acorde * 4):
            nota = notas[padrao[passo % 4]] + 12
            adicionar_nota(buffer, inicio_acorde + passo * tempo_batida / 4,
                           tempo_batida / 4 * 0.7, nota, 0.07, "quadrada", 0.125)
        # "Bumbo" curto no tempo forte de cada batida.
        for batida in range(batidas_por_acorde):
            adicionar_nota(buffer, inicio_acorde + batida * tempo_batida, 0.06, 33, 0.25,
                           "quadrada", 0.5)
    salvar(buffer, "musica_partida.wav", pico=0.20)


if __name__ == "__main__":
    PASTA_SONS.mkdir(parents=True, exist_ok=True)
    musica_menu()
    musica_partida()
