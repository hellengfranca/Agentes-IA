import pygame
import constantes
import random

class AgenteBDI:
    def __init__(self, nome, ambiente, x, y, recursos, base_x, base_y, obstaculos):
        self.nome = nome
        self.ambiente = ambiente
        self.x = x
        self.y = y
        self.base_x = base_x
        self.base_y = base_y
        self.recursos = recursos
        self.obstaculos = obstaculos

        self.crencas = {}
        self.desejos = []
        self.intencao = None

        self.recurso_carregado = None
        self.recursos_entregues = []
        self.carregando_recurso = False
        self.em_tempestade = False
        self.cor = (255, 0, 255)

        self.processo = ambiente.process(self.run())

    def atualizar_crencas(self, agentes):
        for agente in agentes:
            if hasattr(agente, "conhecimento_compartilhado"):
                for (x, y), status in agente.conhecimento_compartilhado.items():
                    if status == "disponível":
                        self.crencas[(x, y)] = status

    def atualizar_desejos(self):
        self.desejos = [
            (x, y) for (x, y) in self.crencas.keys()
            if not self.recurso_ja_coletado(x, y)
        ]

    def escolher_intencao(self):
        if self.desejos:
            self.intencao = random.choice(self.desejos)

    def recurso_ja_coletado(self, x, y):
        for recurso in self.recursos:
            if recurso.x == x and recurso.y == y:
                return recurso.collected
        return True

    def mover_ate(self, destino_x, destino_y):
        while (self.x, self.y) != (destino_x, destino_y):
            dx = destino_x - self.x
            dy = destino_y - self.y
            novo_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            novo_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)
            if (novo_x, novo_y) not in [(o.x, o.y) for o in self.obstaculos]:
                self.x, self.y = novo_x, novo_y
            else:
                self.mover_explorando()
            yield self.ambiente.timeout(1)

    def mover_explorando(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]]
        livres = [
            (nx, ny) for nx, ny in vizinhos
            if 0 <= nx < constantes.GRID_WIDTH and 0 <= ny < constantes.GRID_HEIGHT
            and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
        ]
        if livres:
            self.x, self.y = random.choice(livres)

    def coletar_recurso(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0,0), (0,1),(0,-1),(1,0),(-1,0)]]
        for recurso in self.recursos:
            if not recurso.collected and (recurso.x, recurso.y) in vizinhos:
                if recurso.type in ["cristal", "metais"]:
                    recurso.collected = True
                    self.recurso_carregado = recurso
                    self.carregando_recurso = True
                    return True
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
                self.recursos_entregues.append(self.recurso_carregado)
                self.recurso_carregado = None
                self.carregando_recurso = False

            else:
                self.atualizar_crencas(self.todos_os_agentes)
                self.atualizar_desejos()
                self.escolher_intencao()

                if self.intencao:
                    yield from self.mover_ate(*self.intencao)
                    if self.coletar_recurso():
                        self.intencao = None
                        continue

                self.mover_explorando()

            yield self.ambiente.timeout(1)

    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 255), (self.x * 20, self.y * 20, 20, 20))
        fonte = pygame.font.SysFont("arial", 8)
        letra = fonte.render("B", True, (0, 0, 0))
        tela.blit(letra, (self.x * 20 + 6, self.y * 20 + 2))
