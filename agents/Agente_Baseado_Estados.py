import random
import pygame
import constantes

class AgenteBaseadoEmEstado:
    def __init__(self, nome, ambiente, x, y, recursos, base_x, base_y, obstaculos, agente_cooperativo,agente_bdi):
        self.nome = nome
        self.ambiente = ambiente
        self.x = x
        self.y = y
        self.base_x = base_x
        self.base_y = base_y
        self.recursos = recursos
        self.obstaculos = obstaculos
        self.agente_cooperativo = agente_cooperativo
        self.agente_bdi = agente_bdi
        self.carregando_recurso = False
        self.recurso_carregado = None
        self.pontuacao = 0
        self.conhecimento_compartilhado = {}
        self.em_tempestade = False
        self.recurso_chamado = None

        self.cor = (0, 255, 0)
        self.ambiente.process(self.run())

        # Nova matriz de posições visitadas
        self.visitado = [[False for _ in range(constantes.GRID_HEIGHT)] for _ in range(constantes.GRID_WIDTH)]
        self.visitado[self.x][self.y] = True  # marca posição inicial como visitada

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
        for i in range(5):
            for j in range(5):
                self.visitado[i][j] = True

        yield from self.mover_para_fora_da_base()

        while True:
            if self.em_tempestade:
                yield from self.retornar_para_base()

                if self.agente_bdi:
                    self.agente_bdi.atualizar_visitado(self.visitado)
                    bdi_map = self.agente_bdi.fornecer_visitado()
                    for i in range(constantes.GRID_WIDTH):
                        for j in range(constantes.GRID_HEIGHT):
                            if bdi_map[i][j]:
                                self.visitado[i][j] = True
                                
                self.em_tempestade = False
               
            elif self.carregando_recurso:
                yield from self.retornar_para_base()
                
                if self.agente_bdi:
                    self.agente_bdi.atualizar_visitado(self.visitado)
                    bdi_map = self.agente_bdi.fornecer_visitado()
                    for i in range(constantes.GRID_WIDTH):
                        for j in range(constantes.GRID_HEIGHT):
                            if bdi_map[i][j]:
                                self.visitado[i][j] = True
                
                
                if self.recurso_carregado:
                    self.pontuacao += self.recurso_carregado.value
                    print(f"[ESTADO] Pontuação atual: {self.pontuacao} (coletou {self.recurso_carregado.type})")
                
                self.carregando_recurso = False
                self.recurso_carregado = None
                
                yield from self.mover_para_fora_da_base()  

            elif self.recurso_carregado and self.recurso_carregado.type == "estrutura_antiga":
                if self.recurso_carregado.collected:
                    self.pontuacao += self.recurso_carregado.value
                    print(f"[ESTADO] Pontuação atual: {self.pontuacao} (ajudou com {self.recurso_carregado.type})")
                    self.recurso_carregado = None
                    yield from self.mover_para_fora_da_base()  # fugir da base após ajudar
                else:
                    yield self.ambiente.timeout(1)

            else:
                resultado = yield from self.coletar_recurso()
                if resultado:
                    yield from self.retornar_para_base()
                    if self.recurso_carregado:
                        self.pontuacao += self.recurso_carregado.value
                        print(f"[ESTADO] Pontuação atual: {self.pontuacao} (coletou {self.recurso_carregado.type})")
                    if self.agente_bdi:
                        self.agente_bdi.atualizar_visitado(self.visitado)
                        bdi_map = self.agente_bdi.fornecer_visitado()
                        for i in range(constantes.GRID_WIDTH):
                            for j in range(constantes.GRID_HEIGHT):
                                if bdi_map[i][j]:
                                    self.visitado[i][j] = True
                        
                    self.carregando_recurso = False
                    self.recurso_carregado = None
                    yield from self.mover_para_fora_da_base()
                else:
                    self.mover_explorando()

            yield self.ambiente.timeout(1)


    def mover_explorando(self):
        vizinhos = [(self.x + dx, self.y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]

        movimentos_novos = [
            (nx, ny)
            for nx, ny in vizinhos
            if 0 <= nx < constantes.GRID_WIDTH and 0 <= ny < constantes.GRID_HEIGHT
            and not self.visitado[nx][ny]
            and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
        ]

        if movimentos_novos:
            self.x, self.y = random.choice(movimentos_novos)
            self.visitado[self.x][self.y] = True
        else:
            # Todos já visitados ou bloqueados, tentar qualquer vizinho válido
            alternativas = [
                (nx, ny)
                for nx, ny in vizinhos
                if 0 <= nx < constantes.GRID_WIDTH and 0 <= ny < constantes.GRID_HEIGHT
                and (nx, ny) not in [(o.x, o.y) for o in self.obstaculos]
            ]
            if alternativas:
                self.x, self.y = random.choice(alternativas)
                self.visitado[self.x][self.y] = True

    def mover_para_fora_da_base(self):
        while self.x < 5 or self.y < 5:
            if self.x < constantes.GRID_WIDTH - 1:
                self.x += 1
            if self.y < constantes.GRID_HEIGHT - 1:
                self.y += 1
            self.visitado[self.x][self.y] = True
            yield self.ambiente.timeout(1)



    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 255), (self.x * 20, self.y * 20, 20, 20))
        fonte = pygame.font.SysFont("arial", 8)
        letra = fonte.render("E", True, (0, 0, 0))
        tela.blit(letra, (self.x * 20 + 6, self.y * 20 + 2))
