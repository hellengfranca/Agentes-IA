import random
import pygame
import constantes

class AgenteCoperativo:
    def __init__(self, nome, ambiente, x, y, recursos, base_x, base_y, obstaculos, todos_os_agentes):
        self.nome = nome
        self.ambiente = ambiente
        self.x = x
        self.y = y
        self.base_x = base_x
        self.base_y = base_y
        self.recursos = recursos
        self.obstaculos = obstaculos
        self.todos_os_agentes = todos_os_agentes
        self.resources_collected = 0
        self.recurso_chamado = None
        self.carregando_recurso = False
        self.recurso_carregado = None
        self.recursos_entregues = []
        self.em_tempestade = False
        self.cor = (0, 0, 255)

        self.processo = ambiente.process(self.run())

    def receber_chamada(self, recurso):
        if recurso and not recurso.collected:
            self.recurso_chamado = recurso

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

    def retornar_para_base(self):
        yield from self.mover_ate(self.base_x, self.base_y)
        
    def mover_explorando(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]

        movimentos_validos = [
            (nx, ny)
            for nx, ny in vizinhos
            if 0 <= nx < 20 and 0 <= ny < 20
            and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
        ]

        if movimentos_validos:
            self.x, self.y = random.choice(movimentos_validos)
    
    def coletar_recurso(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0,0), (0,1), (0,-1), (1,0), (-1,0)]]
        print("Cooperativo consertou recurso")
        for recurso in self.recursos:
            if not recurso.collected and (recurso.x, recurso.y) in vizinhos:
                if recurso.type in ["cristal", "metais","estrutura antiga"]:
                    recurso.collected = True
                    self.carregando_recurso = True
                    self.recurso_carregado = recurso
                    self.resources_collected += recurso.value
                    self.x, self.y = recurso.x, recurso.y
                    return True
            return False
    
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
            
            elif self.recurso_chamado and not self.recurso_chamado.collected:
                # Vai até a estrutura
                yield from self.mover_ate(self.recurso_chamado.x, self.recurso_chamado.y)

                # Verifica se há outro agente nas redondezas (distância de 1 bloco)
                agentes_proximos = [
                    agente for agente in self.todos_os_agentes
                    if agente != self
                    and abs(agente.x - self.x) <= 1
                    and abs(agente.y - self.y) <= 1
                ]

                if agentes_proximos:
                    self.recurso_chamado.collected = True
                    self.recursos_entregues.append(self.recurso_chamado)
                    self.recurso_chamado = None
                    yield from self.retornar_para_base()

            else:
                self.mover_explorando()

            yield self.ambiente.timeout(1)


    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 255), (self.x * 20, self.y * 20, 20, 20))
        fonte = pygame.font.SysFont("arial", 8)
        letra = fonte.render("C", True, (0, 0, 0))
        tela.blit(letra, (self.x * 20 + 6, self.y * 20 + 2))
