"""Feedback visual: partículas, tremor de tela e clarão de dano."""
import random

import pygame


class Particula:
    def __init__(self, x, y, cor):
        self.x, self.y = x, y
        angulo_x = random.uniform(-1, 1)
        angulo_y = random.uniform(-1, 1)
        velocidade = random.uniform(60, 220)
        self.vx = angulo_x * velocidade
        self.vy = angulo_y * velocidade
        self.cor = cor
        self.vida = random.uniform(0.35, 0.7)  # segundos até sumir
        self.tamanho = random.choice([3, 4, 5])

    def atualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.9  # atrito: as partículas desaceleram
        self.vy *= 0.9
        self.vida -= dt

    def desenhar(self, superficie):
        tamanho = max(1, int(self.tamanho * min(1.0, self.vida * 2)))
        pygame.draw.rect(superficie, self.cor, (int(self.x), int(self.y), tamanho, tamanho))


class Efeitos:
    def __init__(self):
        self.particulas = []
        self.tremor = 0.0  # segundos restantes de tremor
        self.clarao = 0.0  # segundos restantes do clarão vermelho

    def explosao(self, centro, cores, quantidade=18):
        for _ in range(quantidade):
            self.particulas.append(Particula(centro[0], centro[1], random.choice(cores)))

    def tremer(self, duracao=0.35):
        self.tremor = duracao
        self.clarao = 0.18

    def atualizar(self, dt):
        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if p.vida > 0]
        self.tremor = max(0.0, self.tremor - dt)
        self.clarao = max(0.0, self.clarao - dt)

    def deslocamento(self):
        """Quanto a câmera deve ser deslocada neste quadro (tremor)."""
        if self.tremor <= 0:
            return 0, 0
        forca = int(8 * self.tremor / 0.35) + 1
        return random.randint(-forca, forca), random.randint(-forca, forca)

    def desenhar(self, superficie):
        for p in self.particulas:
            p.desenhar(superficie)
