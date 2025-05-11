import random
import pygame
import constantes

class AgenteBaseadoEmEstado:
    def __init__(self, nome, ambiente, x, y, recursos, base_x, base_y, obstaculos, agente_cooperativo):
        self.nome = nome
        self.ambiente = ambiente
        self.x = x
        self.y = y
        self.base_x = base_x
        self.base_y = base_y
        self.recursos = recursos
        self.obstaculos = obstaculos
        self.agente_cooperativo = agente_cooperativo

        self.posicoes_exploradas = set()
        self.carregando_recurso = False
        self.recurso_carregado = None
        self.recursos_entregues = []
        self.conhecimento_compartilhado = {}
        self.em_tempestade = False
        self.recurso_chamado = None

        self.cor = (0, 255, 0)
        self.processo = ambiente.process(self.run())

    def mover_ate(self, destino_x, destino_y):
        while (self.x, self.y) != (destino_x, destino_y):
            dx = destino_x - self.x
            dy = destino_y - self.y
            proximo_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            proximo_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)

            if (proximo_x, proximo_y) not in [(o.x, o.y) for o in self.obstaculos]:
                self.x, self.y = proximo_x, proximo_y
            else:
                self.mover_explorando()
            yield self.ambiente.timeout(1)

    def coletar_recurso(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0,0), (0,1), (0,-1), (1,0), (-1,0)]]

        for recurso in self.recursos:
            if not recurso.collected and (recurso.x, recurso.y) in vizinhos:
                if recurso.type in ["cristal", "metais"]:
                    recurso.collected = True
                    self.carregando_recurso = True
                    self.recurso_carregado = recurso
                    self.x, self.y = recurso.x, recurso.y
                    return True

                elif recurso.type == "estrutura antiga":
                    self.recurso_carregado = recurso
                    self.recurso_chamado = recurso
                    self.agente_cooperativo.receber_chamada(recurso)
                    yield from self.mover_ate(recurso.x, recurso.y)
                    return False
        return False

    def retornar_para_base(self):
        yield from self.mover_ate(self.base_x, self.base_y)

    def run(self):
        while True:
            if self.em_tempestade:
                yield from self.retornar_para_base()
                self.em_tempestade = False

            elif self.carregando_recurso:
                yield from self.retornar_para_base()
                self.carregando_recurso = False
                self.recursos_entregues.append(self.recurso_carregado)
                self.recurso_carregado = None

            elif self.recurso_carregado and self.recurso_carregado.type == "estrutura antiga":
                if not self.recurso_carregado.collected:
                    yield self.ambiente.timeout(1)
                else:
                    self.recursos_entregues.append(self.recurso_carregado)
                    self.recurso_carregado = None

            else:
                resultado = yield from self.coletar_recurso()
                if resultado:
                    yield from self.retornar_para_base()
                    self.carregando_recurso = False
                    self.recursos_entregues.append(self.recurso_carregado)
                    self.recurso_carregado = None
                else:
                    self.mover_explorando()

            yield self.ambiente.timeout(1)

    def mover_explorando(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]

        movimentos_validos = [
            (nx, ny)
            for nx, ny in vizinhos
            if 0 <= nx < 20 and 0 <= ny < 20
            and (nx, ny) not in self.posicoes_exploradas
            and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
        ]

        if movimentos_validos:
            self.x, self.y = random.choice(movimentos_validos)
            self.posicoes_exploradas.add((self.x, self.y))
        else:
            alternativas = [
                (nx, ny) for nx, ny in vizinhos
                if 0 <= nx < 20 and 0 <= ny < 20
                and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
            ]
            if alternativas:
                self.x, self.y = random.choice(alternativas)

    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 255), (self.x * 20, self.y * 20, 20, 20))
        fonte = pygame.font.SysFont("arial", 8)
        letra = fonte.render("E", True, (0, 0, 0))
        tela.blit(letra, (self.x * 20 + 6, self.y * 20 + 2))
