"""Regras da partida: movimento, colisões, pontuação, energia, vidas e fases."""
import math
import random

import pygame

from .config import ALTURA, ALTURA_HUD, LARGURA, TOTAL_BATERIAS, TOTAL_ROBOS

# Paredes da estação (fixas em todas as partidas).
PAREDES = [
    (220, 95, 160, 32), (440, 190, 32, 150), (160, 290, 190, 32),
    (570, 80, 32, 125), (650, 365, 190, 32), (350, 475, 32, 95),
]

# Perigos de cada fase. Na fase 2 e 3 novos perigos são somados aos anteriores.
# eixo: direção da patrulha; amplitude: distância máxima a partir da base;
# velocidade: rapidez da oscilação; atraso: desencontra os perigos entre si.
PERIGOS_POR_FASE = {
    1: [
        {"tipo": "laser", "base": (110, 220), "tamanho": (120, 8), "eixo": "x", "amplitude": 35, "velocidade": 1.5, "atraso": 0.0},
        {"tipo": "laser", "base": (520, 520), "tamanho": (120, 8), "eixo": "x", "amplitude": 35, "velocidade": 1.5, "atraso": 1.0},
        {"tipo": "drone", "base": (760, 150), "tamanho": (30, 30), "eixo": "y", "amplitude": 70, "velocidade": 1.7, "atraso": 0.0},
    ],
    2: [
        {"tipo": "drone", "base": (300, 410), "tamanho": (30, 30), "eixo": "x", "amplitude": 110, "velocidade": 1.4, "atraso": 2.0},
    ],
    3: [
        {"tipo": "laser", "base": (700, 230), "tamanho": (8, 100), "eixo": "x", "amplitude": 60, "velocidade": 1.2, "atraso": 0.5},
        {"tipo": "drone", "base": (120, 450), "tamanho": (30, 30), "eixo": "y", "amplitude": 60, "velocidade": 2.0, "atraso": 1.0},
    ],
}

# Textos de história mostrados quando o RX-7 chega a uma nova fase.
TEXTOS_FASE = {
    2: ["Os sistemas de defesa detectaram o RX-7.",
        "Um novo drone de segurança foi ativado.",
        "Os perigos agora estão mais rápidos."],
    3: ["Energia da estação em nível crítico!",
        "Um laser vertical e outro drone entraram em ação.",
        "Falta pouco: resgate os últimos robôs."],
}

PONTOS_BATERIA = 10
PONTOS_ROBO = 100


class Perigo:
    """Laser ou drone que patrulha de um lado para o outro."""

    def __init__(self, dados):
        self.tipo = dados["tipo"]
        self.base = dados["base"]
        self.eixo = dados["eixo"]
        self.amplitude = dados["amplitude"]
        self.velocidade = dados["velocidade"]
        self.atraso = dados["atraso"]
        self.rect = pygame.Rect(self.base, dados["tamanho"])
        self.ativo = True

    def area_de_patrulha(self):
        """Retângulo que cobre todo o caminho do perigo (para não pôr itens nele)."""
        if self.eixo == "x":
            area = pygame.Rect(self.base[0] - self.amplitude, self.base[1],
                               self.rect.w + 2 * self.amplitude, self.rect.h)
        else:
            area = pygame.Rect(self.base[0], self.base[1] - self.amplitude,
                               self.rect.w, self.rect.h + 2 * self.amplitude)
        return area.inflate(24, 24)

    def atualizar(self, tempo, multiplicador):
        deslocamento = int(math.sin(tempo * self.velocidade * multiplicador + self.atraso) * self.amplitude)
        if self.eixo == "x":
            self.rect.x = self.base[0] + deslocamento
        else:
            self.rect.y = self.base[1] + deslocamento
        if self.tipo == "laser":
            # O laser fica 2/3 do ciclo ligado e 1/3 desligado (passagem segura).
            self.ativo = (tempo * 2 * multiplicador + self.atraso) % 3 >= 1


class Partida:
    def __init__(self, dificuldade):
        self.dificuldade = dificuldade
        self.jogador = pygame.Rect(64, 80, 32, 32)
        # Posição em ponto flutuante: evita perder frações de pixel no movimento.
        self.posicao = pygame.Vector2(self.jogador.topleft)
        self.saida = pygame.Rect(LARGURA - 96, ALTURA - 100, 48, 48)
        self.paredes = [pygame.Rect(p) for p in PAREDES]
        self.perigos = [Perigo(d) for d in PERIGOS_POR_FASE[1]]

        self.pontos = 0
        self.energia = 100.0
        self.vidas = dificuldade["vidas"]
        self.resgatados = 0
        self.fase = 1
        self.tempo = 0.0
        self.invulneravel = 0.0
        self.andando = False
        self.mensagem = "Resgate os 5 robôs e encontre a saída!"
        self.mensagem_tempo = 4.0
        self.fim = None  # None, "vitoria", "sem_energia" ou "sem_vidas"
        self.nova_fase = None  # avisa o laço principal para mostrar a transição
        self.eventos = []  # sons e efeitos pedidos neste quadro: (nome, posição)
        self._espalhar_itens()

    # ------------------------------------------------------------------ itens
    def _espalhar_itens(self):
        """Sorteia baterias e robôs em espaços livres do mapa."""
        perigos_futuros = [Perigo(d) for fase in PERIGOS_POR_FASE.values() for d in fase]
        zonas_proibidas = [p.inflate(16, 16) for p in self.paredes]
        zonas_proibidas += [self.jogador.inflate(120, 120), self.saida.inflate(60, 60)]
        zonas_de_perigo = [p.area_de_patrulha() for p in perigos_futuros]

        livres, seguros = [], []
        for y in range(104, ALTURA - 72, 64):
            for x in range(64, LARGURA - 64, 64):
                r = pygame.Rect(x, y, 28, 30)
                if r.collidelist(zonas_proibidas) != -1:
                    continue
                livres.append((x, y))
                if r.collidelist(zonas_de_perigo) == -1:
                    seguros.append((x, y))
        random.shuffle(seguros)
        # Robôs nunca ficam dentro da rota de um perigo; baterias podem ficar (risco extra).
        posicoes_robos = seguros[:TOTAL_ROBOS]
        restantes = [p for p in livres if p not in posicoes_robos]
        random.shuffle(restantes)
        self.robos = [pygame.Rect(x, y, 28, 30) for x, y in posicoes_robos]
        self.baterias = [pygame.Rect(x + 3, y + 2, 22, 26) for x, y in restantes[:TOTAL_BATERIAS]]

    # ---------------------------------------------------------------- jogador
    def _mover(self, dx, dy):
        """Move em um eixo por vez e empurra o robô para fora das paredes."""
        self.posicao.x += dx
        self.jogador.x = round(self.posicao.x)
        for parede in self.paredes:
            if self.jogador.colliderect(parede):
                if dx > 0:
                    self.jogador.right = parede.left
                elif dx < 0:
                    self.jogador.left = parede.right
                self.posicao.x = self.jogador.x
        self.posicao.y += dy
        self.jogador.y = round(self.posicao.y)
        for parede in self.paredes:
            if self.jogador.colliderect(parede):
                if dy > 0:
                    self.jogador.bottom = parede.top
                elif dy < 0:
                    self.jogador.top = parede.bottom
                self.posicao.y = self.jogador.y
        # Não deixa sair da área de jogo (abaixo do HUD).
        self.jogador.clamp_ip(pygame.Rect(0, ALTURA_HUD, LARGURA, ALTURA - ALTURA_HUD))
        self.posicao.update(self.jogador.topleft)

    def _aviso(self, texto, duracao):
        self.mensagem = texto
        self.mensagem_tempo = duracao

    def _evento(self, nome, rect=None):
        self.eventos.append((nome, rect.center if rect else None))

    # ------------------------------------------------------------------ regras
    def multiplicador_perigos(self):
        return self.dificuldade["velocidade_perigos"] * (1 + 0.22 * (self.fase - 1))

    def _avancar_fase(self):
        self.fase += 1
        self.perigos += [Perigo(d) for d in PERIGOS_POR_FASE[self.fase]]
        self.energia = min(100.0, self.energia + 20)
        self.invulneravel = 2.0  # tempo para o jogador se adaptar aos novos perigos
        self.nova_fase = self.fase

    def _sofrer_dano(self, perigo):
        if self.invulneravel > 0:
            return
        self.vidas -= 1
        self.energia = max(0.0, self.energia - 15)
        self.invulneravel = 1.5
        nome_perigo = "laser" if perigo.tipo == "laser" else "drone"
        self._aviso(f"Atenção! O RX-7 foi atingido por um {nome_perigo}.", 1.8)
        if perigo.tipo == "laser":
            self._evento("laser", self.jogador)
        self._evento("dano", self.jogador)
        if self.vidas <= 0:
            self.fim = "sem_vidas"
        elif self.energia <= 0:
            self.fim = "sem_energia"

    def atualizar(self, dt, teclas):
        self.eventos = []
        self.tempo += dt
        self.mensagem_tempo = max(0.0, self.mensagem_tempo - dt)
        self.invulneravel = max(0.0, self.invulneravel - dt)

        # A energia cai com o tempo (mais rápido nas fases avançadas).
        self.energia -= dt * self.dificuldade["dreno_energia"] * (1 + 0.25 * (self.fase - 1))
        if self.energia <= 0:
            self.energia = 0.0
            self.fim = "sem_energia"
            return

        velocidade = 190 + (self.fase - 1) * 15
        direita = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]
        esquerda = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
        baixo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        cima = teclas[pygame.K_UP] or teclas[pygame.K_w]
        direcao = pygame.Vector2(int(direita) - int(esquerda), int(baixo) - int(cima))
        self.andando = direcao.length_squared() > 0
        if self.andando:
            direcao = direcao.normalize()  # diagonal não fica mais rápida
            self._mover(direcao.x * velocidade * dt, 0)
            self._mover(0, direcao.y * velocidade * dt)

        for perigo in self.perigos:
            perigo.atualizar(self.tempo, self.multiplicador_perigos())

        self._coletar_itens()

        # Hitbox um pouco menor que o desenho: colisões parecem mais justas.
        corpo = self.jogador.inflate(-6, -6)
        for perigo in self.perigos:
            if perigo.ativo and corpo.colliderect(perigo.rect):
                self._sofrer_dano(perigo)
                break
        if self.fim:
            return

        if self.jogador.colliderect(self.saida):
            if self.resgatados >= TOTAL_ROBOS:
                self.fim = "vitoria"
                self.pontos += int(self.energia) * 2 + self.vidas * 50
            elif self.mensagem_tempo <= 0.3:
                self._aviso("A saída ainda está bloqueada. Resgate os 5 robôs!", 1.5)

    def _coletar_itens(self):
        for bateria in self.baterias[:]:
            if self.jogador.colliderect(bateria):
                self.baterias.remove(bateria)
                self.pontos += PONTOS_BATERIA
                self.energia = min(100.0, self.energia + 22)
                self._aviso("+10 pontos! Bateria coletada: energia recuperada.", 1.2)
                self._evento("coleta", bateria)
        for robo in self.robos[:]:
            if self.jogador.colliderect(robo):
                self.robos.remove(robo)
                self.resgatados += 1
                self.pontos += PONTOS_ROBO
                self.energia = min(100.0, self.energia + 8)
                self._evento("resgate", robo)
                if self.resgatados >= TOTAL_ROBOS:
                    self._aviso("Todos resgatados! A SAÍDA foi liberada!", 3.0)
                    self._evento("saida_liberada", self.saida)
                else:
                    self._aviso(f"+100 pontos! Robô resgatado ({self.resgatados}/5).", 1.8)
                # A cada 2 robôs resgatados a estação reage e a fase avança.
                if self.resgatados in (2, 4):
                    self._avancar_fase()
