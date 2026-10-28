"""Tudo o que é desenhado na tela. O visual pixel art é feito só com retângulos."""
import math

import pygame

from .config import (ALTURA, ALTURA_HUD, AMARELO, AZUL, BRANCO, CIANO, CINZA, CINZA_ESCURO,
                     FUNDO, GRADE, LARGURA, PRETO, ROXO, TAMANHO, TOTAL_ROBOS, VERDE,
                     VERMELHO)

FONTES = {}


def iniciar_fontes():
    """Precisa ser chamada depois de pygame.init()."""
    FONTES["pequena"] = pygame.font.Font(None, 24)
    FONTES["normal"] = pygame.font.Font(None, 30)
    FONTES["grande"] = pygame.font.Font(None, 44)
    FONTES["titulo"] = pygame.font.Font(None, 76)


def texto(sup, conteudo, fonte, cor, centro, sombra=True):
    """Escreve um texto centralizado, com sombra para melhorar a leitura."""
    fonte = FONTES[fonte]
    if sombra:
        imagem_sombra = fonte.render(str(conteudo), True, PRETO)
        sup.blit(imagem_sombra, imagem_sombra.get_rect(center=(centro[0] + 2, centro[1] + 2)))
    imagem = fonte.render(str(conteudo), True, cor)
    sup.blit(imagem, imagem.get_rect(center=centro))


def texto_esquerda(sup, conteudo, fonte, cor, posicao):
    imagem = FONTES[fonte].render(str(conteudo), True, cor)
    sup.blit(imagem, imagem.get_rect(midleft=posicao))
    return imagem.get_width()


def caixa(sup, retangulo, cor_borda=(30, 53, 95), alfa=225):
    """Painel escuro semitransparente com moldura pixelada (usado em todas as telas)."""
    painel = pygame.Surface(retangulo.size, pygame.SRCALPHA)
    painel.fill((6, 10, 26, alfa))
    sup.blit(painel, retangulo.topleft)
    pygame.draw.rect(sup, cor_borda, retangulo, 4)
    for canto in (retangulo.topleft, retangulo.topright, retangulo.bottomleft, retangulo.bottomright):
        pygame.draw.rect(sup, CIANO, (canto[0] - 4, canto[1] - 4, 8, 8))


# ------------------------------------------------------------------ cenário
def desenhar_fundo(sup, tempo=0.0):
    sup.fill(FUNDO)
    for x in range(0, LARGURA, TAMANHO):
        pygame.draw.line(sup, GRADE, (x, 0), (x, ALTURA), 1)
    for y in range(0, ALTURA, TAMANHO):
        pygame.draw.line(sup, GRADE, (0, y), (LARGURA, y), 1)
    # Luzes da estação piscando em tempos diferentes.
    for i in range(42):
        x = (i * 137 + 29) % LARGURA
        y = (i * 83 + 17) % ALTURA
        acesa = math.sin(tempo * 2 + i) > 0.6
        cor = (90, 150, 210) if acesa else ((38, 62, 104) if i % 3 else (65, 111, 160))
        pygame.draw.rect(sup, cor, (x, y, 3, 3))


def desenhar_parede(sup, parede):
    pygame.draw.rect(sup, (42, 57, 91), parede)
    pygame.draw.rect(sup, (92, 121, 166), (parede.x, parede.y, parede.w, 5))
    if parede.w >= parede.h:
        for px in range(parede.x + 10, parede.right - 5, 20):
            pygame.draw.rect(sup, (25, 38, 68), (px, parede.y + 10, 8, max(4, parede.h - 15)))
    else:
        for py in range(parede.y + 12, parede.bottom - 8, 20):
            pygame.draw.rect(sup, (25, 38, 68), (parede.x + 8, py, parede.w - 16, 8))


def desenhar_saida(sup, saida, liberada, tempo):
    if liberada:
        # Brilho pulsante para chamar o jogador.
        pulso = int(6 + 4 * math.sin(tempo * 6))
        pygame.draw.rect(sup, (30, 90, 70), saida.inflate(12 + pulso, 12 + pulso), 3)
    cor = VERDE if liberada else CINZA_ESCURO
    pygame.draw.rect(sup, (25, 40, 66), saida.inflate(12, 12))
    pygame.draw.rect(sup, cor, saida, 4)
    pygame.draw.rect(sup, cor, (saida.x + 12, saida.y + 8, 24, 32), 3)
    if not liberada:
        # Cadeado: a saída está trancada.
        pygame.draw.rect(sup, cor, (saida.centerx - 6, saida.centery - 2, 12, 10))
        pygame.draw.rect(sup, cor, (saida.centerx - 4, saida.centery - 8, 8, 7), 2)
    texto(sup, "SAÍDA", "pequena", cor, (saida.centerx, saida.bottom + 18))


# ------------------------------------------------------------- personagens
def desenhar_robo(sup, x, y, cor=AZUL, escala=1, quadro=0, olhos=PRETO):
    """Robô em blocos. `quadro` alterna as pernas (animação de andar)."""
    s = escala
    perna_esq = 2 * s if quadro == 1 else 0
    perna_dir = 2 * s if quadro == 2 else 0
    pygame.draw.rect(sup, (8, 14, 32), (x + 4 * s, y + 5 * s, 24 * s, 23 * s))
    pygame.draw.rect(sup, cor, (x + 5 * s, y + 4 * s, 22 * s, 20 * s))
    pygame.draw.rect(sup, (180, 225, 255), (x + 8 * s, y + 7 * s, 16 * s, 5 * s))
    pygame.draw.rect(sup, olhos, (x + 9 * s, y + 13 * s, 4 * s, 5 * s))
    pygame.draw.rect(sup, olhos, (x + 19 * s, y + 13 * s, 4 * s, 5 * s))
    pygame.draw.rect(sup, cor, (x + 1 * s, y + 10 * s - perna_dir, 4 * s, 10 * s))
    pygame.draw.rect(sup, cor, (x + 27 * s, y + 10 * s - perna_esq, 4 * s, 10 * s))
    pygame.draw.rect(sup, (80, 110, 150), (x + 8 * s, y + 24 * s - perna_esq, 5 * s, 6 * s))
    pygame.draw.rect(sup, (80, 110, 150), (x + 19 * s, y + 24 * s - perna_dir, 5 * s, 6 * s))
    pygame.draw.rect(sup, AMARELO, (x + 14 * s, y + 1 * s, 4 * s, 3 * s))


def desenhar_jogador(sup, partida):
    # Pisca enquanto está invulnerável depois de levar dano.
    if partida.invulneravel > 0 and int(partida.tempo * 12) % 2 == 1:
        return
    quadro = 0
    if partida.andando:
        quadro = 1 if int(partida.tempo * 8) % 2 == 0 else 2
    desenhar_robo(sup, partida.jogador.x, partida.jogador.y, AZUL, quadro=quadro)


def desenhar_robo_preso(sup, robo, tempo, indice):
    # Robôs presos "pulam" pedindo ajuda e mostram um sinal de SOS.
    salto = int(abs(math.sin(tempo * 4 + indice)) * 4)
    desenhar_robo(sup, robo.x - 2, robo.y - salto, ROXO, olhos=(60, 20, 90))
    if int(tempo * 2 + indice) % 2 == 0:
        texto(sup, "SOS", "pequena", (220, 190, 255), (robo.centerx, robo.y - 14), sombra=False)


def desenhar_bateria(sup, rect, tempo):
    brilho = 3 if int(tempo * 4) % 2 == 0 else 1
    x, y = rect.x, rect.y
    pygame.draw.rect(sup, (20, 70, 65), (x - brilho, y - brilho, rect.w + 2 * brilho, rect.h + 2 * brilho))
    pygame.draw.rect(sup, VERDE, rect)
    pygame.draw.rect(sup, (210, 255, 214), (x + 5, y + 4, 6, rect.h - 8))
    pygame.draw.rect(sup, (210, 255, 214), (x + 13, y + 4, 4, rect.h - 8))
    pygame.draw.rect(sup, VERDE, (x + rect.w, y + 6, 4, rect.h - 12))


def desenhar_perigo(sup, perigo, tempo):
    r = perigo.rect
    if perigo.tipo == "laser":
        pygame.draw.rect(sup, (70, 28, 57), r.inflate(8, 8))
        if perigo.ativo:
            pygame.draw.rect(sup, VERMELHO, r)
            # Linha central tremendo dá sensação de energia.
            if r.w >= r.h:
                y = r.centery + (1 if int(tempo * 30) % 2 else -1)
                pygame.draw.line(sup, (255, 190, 200), (r.left, y), (r.right, y), 2)
            else:
                x = r.centerx + (1 if int(tempo * 30) % 2 else -1)
                pygame.draw.line(sup, (255, 190, 200), (x, r.top), (x, r.bottom), 2)
        else:
            pygame.draw.rect(sup, (100, 35, 65), r, 2)
        # Emissores nas pontas.
        if r.w >= r.h:
            pygame.draw.rect(sup, CINZA, (r.left - 6, r.centery - 6, 6, 12))
            pygame.draw.rect(sup, CINZA, (r.right, r.centery - 6, 6, 12))
        else:
            pygame.draw.rect(sup, CINZA, (r.centerx - 6, r.top - 6, 12, 6))
            pygame.draw.rect(sup, CINZA, (r.centerx - 6, r.bottom, 12, 6))
    else:
        # Drone: corpo, olho vermelho e hélices animadas (2 quadros).
        pygame.draw.rect(sup, (40, 30, 50), r.inflate(4, 4))
        pygame.draw.rect(sup, (150, 70, 90), r)
        pygame.draw.rect(sup, (90, 40, 60), (r.x + 3, r.y + r.h - 8, r.w - 6, 5))
        olho = VERMELHO if int(tempo * 6) % 2 == 0 else (255, 180, 120)
        pygame.draw.rect(sup, PRETO, (r.centerx - 7, r.y + 8, 14, 10))
        pygame.draw.rect(sup, olho, (r.centerx - 4, r.y + 10, 8, 6))
        largura = 18 if int(tempo * 20) % 2 == 0 else 8
        for lado in (r.left + 2, r.right - 2):
            pygame.draw.line(sup, CINZA, (lado, r.y), (lado, r.y - 5), 2)
            pygame.draw.line(sup, BRANCO, (lado - largura // 2, r.y - 6), (lado + largura // 2, r.y - 6), 2)


# --------------------------------------------------------------------- HUD
def desenhar_coracao(sup, x, y, cor):
    for dx, dy, w, h in ((2, 0, 4, 2), (8, 0, 4, 2), (0, 2, 14, 6), (2, 8, 10, 2), (4, 10, 6, 2), (6, 12, 2, 2)):
        pygame.draw.rect(sup, cor, (x + dx, y + dy, w, h))


def desenhar_hud(sup, partida, recorde, audio):
    pygame.draw.rect(sup, (6, 10, 24), (0, 0, LARGURA, ALTURA_HUD))
    pygame.draw.line(sup, (30, 53, 95), (0, ALTURA_HUD - 1), (LARGURA, ALTURA_HUD - 1), 2)
    meio = ALTURA_HUD // 2
    texto_esquerda(sup, f"PONTOS {partida.pontos}", "normal", BRANCO, (14, meio))
    texto_esquerda(sup, f"ROBÔS {partida.resgatados}/{TOTAL_ROBOS}", "normal", CIANO, (170, meio))
    texto_esquerda(sup, "VIDAS", "pequena", VERMELHO, (300, meio))
    for i in range(partida.dificuldade["vidas"]):
        cor = VERMELHO if i < partida.vidas else (60, 40, 55)
        desenhar_coracao(sup, 356 + i * 18, meio - 7, cor)
    texto_esquerda(sup, "ENERGIA", "pequena", BRANCO, (444, meio))
    pygame.draw.rect(sup, (65, 40, 60), (520, meio - 8, 120, 16))
    energia = partida.energia
    cor = VERDE if energia > 35 else AMARELO if energia > 15 else VERMELHO
    # Barra pisca quando a energia está crítica.
    if energia > 15 or int(partida.tempo * 6) % 2 == 0:
        pygame.draw.rect(sup, cor, (520, meio - 8, int(120 * max(0, energia) / 100), 16))
    pygame.draw.rect(sup, BRANCO, (520, meio - 8, 120, 16), 1)
    texto_esquerda(sup, f"FASE {partida.fase}", "pequena", AMARELO, (656, meio))
    minutos, segundos = divmod(int(partida.tempo), 60)
    texto_esquerda(sup, f"{minutos:02d}:{segundos:02d}", "pequena", BRANCO, (722, meio))
    texto_esquerda(sup, f"REC {recorde}", "pequena", ROXO, (782, meio))
    texto_esquerda(sup, audio.descricao(), "pequena", CINZA, (866, meio - 9))
    texto_esquerda(sup, "P: pausa", "pequena", CINZA, (866, meio + 9))


def desenhar_partida(sup, mundo, partida, efeitos, recorde, audio):
    """Desenha o mundo numa camada separada para poder 'tremer' a câmera."""
    desenhar_fundo(mundo, partida.tempo)
    desenhar_saida(mundo, partida.saida, partida.resgatados >= TOTAL_ROBOS, partida.tempo)
    for parede in partida.paredes:
        desenhar_parede(mundo, parede)
    for bateria in partida.baterias:
        desenhar_bateria(mundo, bateria, partida.tempo)
    for indice, robo in enumerate(partida.robos):
        desenhar_robo_preso(mundo, robo, partida.tempo, indice)
    for perigo in partida.perigos:
        desenhar_perigo(mundo, perigo, partida.tempo)
    desenhar_jogador(mundo, partida)
    efeitos.desenhar(mundo)

    sup.fill(PRETO)
    sup.blit(mundo, efeitos.deslocamento())
    if efeitos.clarao > 0:
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((255, 40, 60, int(110 * efeitos.clarao / 0.18)))
        sup.blit(camada, (0, 0))

    desenhar_hud(sup, partida, recorde, audio)
    if partida.mensagem_tempo > 0:
        faixa = pygame.Rect(150, ALTURA_HUD + 8, LARGURA - 300, 32)
        caixa(sup, faixa, alfa=170)
        texto(sup, partida.mensagem, "pequena", AMARELO, faixa.center)
    if partida.resgatados < TOTAL_ROBOS:
        texto(sup, "Resgate todos os robôs para liberar a saída", "pequena", CINZA,
              (LARGURA // 2, ALTURA - 14))
    elif int(partida.tempo * 3) % 2 == 0:
        texto(sup, "SAÍDA LIBERADA! Leve o RX-7 até a saída", "pequena", VERDE,
              (LARGURA // 2, ALTURA - 14))


# ------------------------------------------------------------------- telas
def escurecer(sup, alfa=190):
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada.fill((3, 7, 20, alfa))
    sup.blit(camada, (0, 0))


def desenhar_menu(sup, tempo, dificuldade, recorde):
    desenhar_fundo(sup, tempo)
    caixa(sup, pygame.Rect(110, 50, 740, 540))
    flutuar = int(math.sin(tempo * 2.5) * 6)
    quadro = 1 if int(tempo * 4) % 2 == 0 else 2
    desenhar_robo(sup, LARGURA // 2 - 32, 90 + flutuar, AZUL, 2, quadro)
    texto(sup, "ROBO RESGATE", "titulo", CIANO, (LARGURA // 2, 205))
    texto(sup, "MISSÃO RX-7: SALVAR A TRIPULAÇÃO DA ESTAÇÃO ORION", "normal", BRANCO, (LARGURA // 2, 250))
    if int(tempo * 2) % 2 == 0:
        texto(sup, "ENTER - JOGAR", "grande", VERDE, (LARGURA // 2, 305))
    texto(sup, f"<  DIFICULDADE: {dificuldade['nome']}  >", "normal", AMARELO, (LARGURA // 2, 352))
    texto(sup, f"vidas: {dificuldade['vidas']}   ·   setas esquerda/direita para trocar", "pequena", CINZA, (LARGURA // 2, 378))
    texto(sup, f"RECORDE: {recorde}", "normal", ROXO, (LARGURA // 2, 415))
    texto(sup, "COMO JOGAR", "normal", CIANO, (LARGURA // 2, 460))
    texto(sup, "Setas/WASD: mover   P ou ESC: pausar   M: som   - / +: volume", "pequena", BRANCO, (LARGURA // 2, 490))
    texto(sup, "Colete baterias (+10), resgate 5 robôs (+100) e alcance a saída.", "pequena", BRANCO, (LARGURA // 2, 515))
    texto(sup, "Evite lasers vermelhos e drones. Sem energia ou sem vidas, a missão falha.", "pequena", BRANCO, (LARGURA // 2, 540))
    texto(sup, "ESC - sair do jogo", "pequena", CINZA, (LARGURA // 2, 568))


def desenhar_introducao(sup, tempo):
    desenhar_fundo(sup, tempo)
    caixa(sup, pygame.Rect(100, 80, 760, 480), cor_borda=(90, 70, 40))
    if int(tempo * 3) % 2 == 0:
        texto(sup, "! TRANSMISSÃO DE EMERGÊNCIA !", "grande", AMARELO, (LARGURA // 2, 130))
    else:
        texto(sup, "TRANSMISSÃO DE EMERGÊNCIA", "grande", AMARELO, (LARGURA // 2, 130))
    desenhar_robo(sup, 160, 190, AZUL, 2)
    linhas = [
        ("RX-7, aqui é o sistema central da estação ORION.", BRANCO),
        ("Uma pane cortou a energia de todos os setores.", BRANCO),
        ("Cinco robôs de manutenção ficaram presos.", BRANCO),
        ("Os lasers e drones de segurança estão com defeito", VERMELHO),
        ("e atacam qualquer coisa que se mova.", VERMELHO),
    ]
    for i, (linha, cor) in enumerate(linhas):
        texto_esquerda(sup, linha, "normal", cor, (250, 200 + i * 32))
    texto(sup, "Colete baterias para não ficar sem energia.", "normal", CIANO, (LARGURA // 2, 395))
    texto(sup, "A saída só abrirá quando todos forem resgatados.", "normal", CIANO, (LARGURA // 2, 428))
    texto(sup, "Você é nossa última unidade operacional.", "normal", ROXO, (LARGURA // 2, 461))
    texto(sup, "ENTER - iniciar a missão     ESC - voltar", "grande", VERDE, (LARGURA // 2, 515))


def desenhar_transicao(sup, fase, linhas):
    escurecer(sup, 200)
    caixa(sup, pygame.Rect(150, 170, 660, 300), cor_borda=(90, 70, 40))
    texto(sup, f"FASE {fase}", "titulo", AMARELO, (LARGURA // 2, 230))
    texto(sup, "TRANSMISSÃO DA ORION", "pequena", CINZA, (LARGURA // 2, 272))
    for i, linha in enumerate(linhas):
        texto(sup, linha, "normal", BRANCO, (LARGURA // 2, 315 + i * 32))
    texto(sup, "ENTER - continuar", "normal", VERDE, (LARGURA // 2, 438))


def desenhar_pausa(sup):
    escurecer(sup, 190)
    caixa(sup, pygame.Rect(220, 180, 520, 280))
    texto(sup, "PAUSADO", "titulo", CIANO, (LARGURA // 2, 240))
    texto(sup, "P ou ESC - continuar", "normal", BRANCO, (LARGURA // 2, 300))
    texto(sup, "ENTER - voltar ao menu", "normal", BRANCO, (LARGURA // 2, 335))
    texto(sup, "M - ligar/desligar som     - / + volume", "normal", BRANCO, (LARGURA // 2, 370))
    texto(sup, "R - reiniciar a missão", "normal", BRANCO, (LARGURA // 2, 405))


FINAIS = {
    "vitoria": ("MISSÃO CUMPRIDA!", VERDE, [
        "Os cinco robôs foram resgatados e deixaram a ORION.",
        "Com a tripulação reunida, a estação volta a funcionar.",
    ]),
    "sem_energia": ("SEM ENERGIA", AMARELO, [
        "A bateria do RX-7 se esgotou no meio da estação.",
        "No escuro, os robôs presos aguardam um novo resgate...",
    ]),
    "sem_vidas": ("RX-7 DESTRUÍDO", VERMELHO, [
        "As defesas com defeito danificaram o RX-7 demais.",
        "A ORION ficou em silêncio mais uma vez.",
    ]),
}


def desenhar_fim(sup, partida, tempo, novo_recorde, recorde):
    escurecer(sup, 215)
    titulo, cor, linhas = FINAIS[partida.fim]
    caixa(sup, pygame.Rect(120, 90, 720, 470), cor_borda=cor)
    texto(sup, titulo, "titulo", cor, (LARGURA // 2, 150))
    if partida.fim == "vitoria":
        # Os robôs resgatados comemoram pulando.
        for i in range(TOTAL_ROBOS + 1):
            salto = int(abs(math.sin(tempo * 5 + i)) * 10)
            cor_robo = AZUL if i == 2 else ROXO
            desenhar_robo(sup, LARGURA // 2 - 150 + i * 50, 200 - salto, cor_robo)
    else:
        # RX-7 apagado, com faíscas.
        desenhar_robo(sup, LARGURA // 2 - 32, 180, CINZA_ESCURO, 2, olhos=(40, 40, 50))
        if int(tempo * 4) % 2 == 0:
            pygame.draw.rect(sup, AMARELO, (LARGURA // 2 + 24, 184, 4, 4))
    for i, linha in enumerate(linhas):
        texto(sup, linha, "normal", BRANCO, (LARGURA // 2, 275 + i * 32))
    minutos, segundos = divmod(int(partida.tempo), 60)
    texto(sup, f"Pontuação final: {partida.pontos}", "grande", AMARELO, (LARGURA // 2, 360))
    texto(sup, f"Robôs resgatados: {partida.resgatados}/{TOTAL_ROBOS}    Tempo: {minutos:02d}:{segundos:02d}",
          "normal", CIANO, (LARGURA // 2, 400))
    if novo_recorde:
        if int(tempo * 4) % 2 == 0:
            texto(sup, "NOVO RECORDE!", "grande", ROXO, (LARGURA // 2, 445))
    else:
        texto(sup, f"Recorde: {recorde}", "normal", ROXO, (LARGURA // 2, 445))
    texto(sup, "R - jogar novamente     ENTER - menu     ESC - sair", "normal", BRANCO, (LARGURA // 2, 510))
