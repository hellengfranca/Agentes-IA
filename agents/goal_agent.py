import constantes
import random
import pygame

class GoalAgent:
    def __init__(self, nome, ambiente, x, y, recursos, base_x, base_y, obstaculos):
        self.nome = nome
        self.ambiente = ambiente
        self.x = x
        self.y = y
        self.base_x = base_x
        self.base_y = base_y
        self.recursos = recursos
        self.obstaculos = obstaculos
        self.resources_collected = 0
        self.em_tempestade = False
        self.conhecimento_compartilhado = {}  # Novo atributo
        self.cor = (255, 255, 0)
        self.carregandoRecurso = False
        self.processo = ambiente.process(self.run())

    def mover_ate(self, destino_x, destino_y):
        while (self.x, self.y) != (destino_x, destino_y):
            dx = destino_x - self.x
            dy = destino_y - self.y
            proximo_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            proximo_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)

            if (proximo_x, proximo_y) not in [(obs.x, obs.y) for obs in self.obstaculos]:
                self.x, self.y = proximo_x, proximo_y
            else:
                self.mover_explorando()

            yield self.ambiente.timeout(1)

    def mover_explorando(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]]
        livres = [
            (nx, ny) for nx, ny in vizinhos
            if 0 <= nx < constantes.GRID_WIDTH and 0 <= ny < constantes.GRID_HEIGHT
            and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
        ]
        if livres:
            self.x, self.y = random.choice(livres)

    def encontrar_recurso_mais_proximo(self):
        min_dist = float('inf')
        alvo = None
        for recurso in self.recursos:
            if not recurso.collected and recurso.type in ["cristal", "metais"]:
                dist = abs(recurso.x - self.x) + abs(recurso.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    alvo = recurso
        return alvo

    def coletar_recurso(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0,0), (0,1), (0,-1), (1,0), (-1,0)]]
        for recurso in self.recursos:
            if not recurso.collected and (recurso.x, recurso.y) in vizinhos:
                if recurso.type in ["cristal", "metais"]:
                    self.conhecimento_compartilhado[(recurso.x, recurso.y)] = "disponível"
                    recurso.collected = True
                    self.carregandoRecurso = True
                    self.resources_collected += recurso.value
                    self.retornar_para_base()
                    return True

        
        return False

    def retornar_para_base(self):
        self.carregandoRecurso = False
        yield from self.mover_ate(self.base_x, self.base_y)
        
    def run(self):
        while True:
            if self.em_tempestade:
                yield from self.retornar_para_base()
                self.em_tempestade = False

            if self.carregandoRecurso:
                yield from self.retornar_para_base()
                self.carregandoRecurso = False
            else:
                alvo = self.encontrar_recurso_mais_proximo()
                if alvo:
                    yield from self.mover_ate(alvo.x, alvo.y)
                    self.coletar_recurso()
                else:
                    self.mover_explorando()

            yield self.ambiente.timeout(1)
    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 255), (self.x * 20, self.y * 20, 20, 20))
        fonte = pygame.font.SysFont("arial", 8)
        letra = fonte.render("O", True, (0, 0, 0))
        tela.blit(letra, (self.x * 20 + 6, self.y * 20 + 2))
