import pygame
import constantes

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

        self.visitado = [[False for _ in range(constantes.GRID_HEIGHT)] for _ in range(constantes.GRID_WIDTH)]
        self.cor = (255, 0, 255)
        self.processo = ambiente.process(self.run())
        self.em_tempestade = False
    def atualizar_visitado(self, outro_grid):
        for i in range(constantes.GRID_WIDTH):
            for j in range(constantes.GRID_HEIGHT):
                if outro_grid[i][j]:
                    self.visitado[i][j] = True

    def fornecer_visitado(self):
        return self.visitado

    def run(self):
        # Fica parado na base, recebendo e compartilhando conhecimento
        while True:
            yield self.ambiente.timeout(1)

    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 255), (self.x * 20, self.y * 20, 20, 20))
        fonte = pygame.font.SysFont("arial", 8)
        letra = fonte.render("B", True, (0, 0, 0))
        tela.blit(letra, (self.x * 20 + 6, self.y * 20 + 2))
