"""Efeitos sonoros, músicas de fundo, volume e opção de silenciar."""
import pygame

from .config import PASTA_SONS

EFEITOS = ["coleta", "resgate", "dano", "vitoria", "derrota", "inicio", "laser"]
MUSICAS = {"menu": "musica_menu.wav", "partida": "musica_partida.wav"}


class Audio:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.disponivel = True
        except pygame.error:
            # Sem placa de som o jogo continua funcionando, só que mudo.
            self.disponivel = False
        self.volume = 0.7  # volume geral, de 0.0 a 1.0
        self.mudo = False
        self.musica_atual = None
        self.efeitos = {nome: self._carregar(f"{nome}.wav") for nome in EFEITOS}
        self._aplicar_volume()

    def _carregar(self, arquivo):
        caminho = PASTA_SONS / arquivo
        if not self.disponivel or not caminho.exists():
            return None
        try:
            return pygame.mixer.Sound(str(caminho))
        except pygame.error:
            return None

    def _aplicar_volume(self):
        if not self.disponivel:
            return
        efetivo = 0.0 if self.mudo else self.volume
        for som in self.efeitos.values():
            if som:
                som.set_volume(efetivo)
        # A música fica mais baixa que os efeitos para não abafar o feedback.
        pygame.mixer.music.set_volume(efetivo * 0.55)

    def tocar(self, nome):
        som = self.efeitos.get(nome)
        if som and not self.mudo:
            som.play()

    def musica(self, nome):
        """Troca a trilha de fundo (None para silêncio). Repete em loop."""
        if not self.disponivel or nome == self.musica_atual:
            return
        self.musica_atual = nome
        if nome is None:
            pygame.mixer.music.fadeout(400)
            return
        caminho = PASTA_SONS / MUSICAS[nome]
        if not caminho.exists():
            return
        try:
            pygame.mixer.music.load(str(caminho))
            pygame.mixer.music.play(loops=-1, fade_ms=600)
            self._aplicar_volume()
        except pygame.error:
            pass

    def pausar_musica(self, pausada):
        if self.disponivel:
            if pausada:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()

    def alternar_mudo(self):
        self.mudo = not self.mudo
        self._aplicar_volume()

    def mudar_volume(self, delta):
        self.volume = round(min(1.0, max(0.0, self.volume + delta)), 1)
        self.mudo = False
        self._aplicar_volume()
        self.tocar("coleta")  # amostra do novo volume

    def descricao(self):
        if self.mudo:
            return "SOM: MUDO"
        return f"VOL: {int(self.volume * 100)}%"
