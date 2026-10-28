"""Laço principal e máquina de estados (menu, introdução, partida, pausa, fim)."""
import sys

import pygame

from . import desenho
from .audio import Audio
from .config import (ALTURA, AMARELO, CIANO, DIFICULDADE_PADRAO, DIFICULDADES, FPS, LARGURA,
                     ROXO, VERDE, VERMELHO)
from .efeitos import Efeitos
from .partida import TEXTOS_FASE, Partida
from .recorde import carregar_recorde, salvar_recorde

TEMPO_TRANSICAO = 4.0  # segundos que o texto de nova fase fica na tela


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Robo Resgate - RX-7")
        self.mundo = pygame.Surface((LARGURA, ALTURA))  # camada do cenário (para o tremor)
        self.relogio = pygame.time.Clock()
        desenho.iniciar_fontes()
        self.audio = Audio()
        self.efeitos = Efeitos()
        self.recorde = carregar_recorde()
        self.indice_dificuldade = DIFICULDADE_PADRAO
        self.estado = "menu"
        self.partida = None
        self.tempo_tela = 0.0  # relógio usado nas animações das telas
        self.tempo_transicao = 0.0
        self.novo_recorde = False
        self.executando = True
        self.audio.musica("menu")

    # -------------------------------------------------------------- ações
    def iniciar_partida(self):
        self.partida = Partida(DIFICULDADES[self.indice_dificuldade])
        self.efeitos = Efeitos()
        self.novo_recorde = False
        self.estado = "jogando"
        self.audio.tocar("inicio")
        self.audio.musica("partida")

    def ir_para_menu(self):
        self.estado = "menu"
        self.audio.pausar_musica(False)
        self.audio.musica("menu")

    def terminar_partida(self):
        self.estado = "fim"
        self.audio.musica(None)
        self.audio.tocar("vitoria" if self.partida.fim == "vitoria" else "derrota")
        if self.partida.pontos > self.recorde:
            self.recorde = self.partida.pontos
            self.novo_recorde = True
            salvar_recorde(self.recorde)

    # ------------------------------------------------------------ entrada
    def tratar_tecla(self, tecla):
        # Teclas de som funcionam em qualquer tela.
        if tecla == pygame.K_m:
            self.audio.alternar_mudo()
            return
        if tecla in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.audio.mudar_volume(-0.1)
            return
        if tecla in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            self.audio.mudar_volume(0.1)
            return

        if self.estado == "menu":
            if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.estado = "intro"
            elif tecla in (pygame.K_LEFT, pygame.K_a):
                self.indice_dificuldade = (self.indice_dificuldade - 1) % len(DIFICULDADES)
                self.audio.tocar("coleta")
            elif tecla in (pygame.K_RIGHT, pygame.K_d):
                self.indice_dificuldade = (self.indice_dificuldade + 1) % len(DIFICULDADES)
                self.audio.tocar("coleta")
            elif tecla == pygame.K_ESCAPE:
                self.executando = False
        elif self.estado == "intro":
            if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.iniciar_partida()
            elif tecla == pygame.K_ESCAPE:
                self.estado = "menu"
        elif self.estado == "jogando":
            if tecla in (pygame.K_p, pygame.K_ESCAPE):
                self.estado = "pausa"
                self.audio.pausar_musica(True)
        elif self.estado == "transicao":
            if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.estado = "jogando"
        elif self.estado == "pausa":
            if tecla in (pygame.K_p, pygame.K_ESCAPE):
                self.estado = "jogando"
                self.audio.pausar_musica(False)
            elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.ir_para_menu()
            elif tecla == pygame.K_r:
                self.audio.pausar_musica(False)
                self.iniciar_partida()
        elif self.estado == "fim":
            if tecla == pygame.K_r:
                self.iniciar_partida()
            elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.ir_para_menu()
            elif tecla == pygame.K_ESCAPE:
                self.executando = False

    # --------------------------------------------------------- atualização
    def reagir_aos_eventos_da_partida(self):
        """Transforma o que aconteceu nas regras em som e efeito visual."""
        for nome, posicao in self.partida.eventos:
            if nome == "coleta":
                self.audio.tocar("coleta")
                self.efeitos.explosao(posicao, [VERDE, (210, 255, 214)], 14)
            elif nome == "resgate":
                self.audio.tocar("resgate")
                self.efeitos.explosao(posicao, [ROXO, CIANO, (220, 190, 255)], 26)
            elif nome == "dano":
                self.audio.tocar("dano")
                self.efeitos.tremer()
                self.efeitos.explosao(posicao, [VERMELHO, AMARELO], 20)
            elif nome == "laser":
                self.audio.tocar("laser")
            elif nome == "saida_liberada":
                self.audio.tocar("inicio")
                self.efeitos.explosao(posicao, [VERDE, CIANO], 30)

    def atualizar(self, dt):
        self.tempo_tela += dt
        if self.estado == "jogando":
            teclas = pygame.key.get_pressed()
            self.partida.atualizar(dt, teclas)
            self.reagir_aos_eventos_da_partida()
            self.efeitos.atualizar(dt)
            if self.partida.fim:
                self.terminar_partida()
            elif self.partida.nova_fase:
                self.estado = "transicao"
                self.tempo_transicao = TEMPO_TRANSICAO
                self.partida.nova_fase = None
        elif self.estado == "transicao":
            self.efeitos.atualizar(dt)
            self.tempo_transicao -= dt
            if self.tempo_transicao <= 0:
                self.estado = "jogando"
        elif self.estado == "fim":
            self.efeitos.atualizar(dt)

    # -------------------------------------------------------------- desenho
    def desenhar(self):
        if self.estado == "menu":
            desenho.desenhar_menu(self.tela, self.tempo_tela, DIFICULDADES[self.indice_dificuldade],
                                  self.recorde)
        elif self.estado == "intro":
            desenho.desenhar_introducao(self.tela, self.tempo_tela)
        else:
            desenho.desenhar_partida(self.tela, self.mundo, self.partida, self.efeitos,
                                     self.recorde, self.audio)
            if self.estado == "transicao":
                fase = self.partida.fase
                desenho.desenhar_transicao(self.tela, fase, TEXTOS_FASE[fase])
            elif self.estado == "pausa":
                desenho.desenhar_pausa(self.tela)
            elif self.estado == "fim":
                desenho.desenhar_fim(self.tela, self.partida, self.tempo_tela, self.novo_recorde,
                                     self.recorde)
        pygame.display.flip()

    def executar(self):
        while self.executando:
            # dt limitado: se a janela travar por um instante, nada "teleporta".
            dt = min(self.relogio.tick(FPS) / 1000.0, 0.04)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.executando = False
                elif evento.type == pygame.KEYDOWN:
                    self.tratar_tecla(evento.key)
            self.atualizar(dt)
            self.desenhar()
        pygame.quit()
        sys.exit()


def main():
    Jogo().executar()
