import resources
import random
import pygame
import constantes
class SimpleAgent:
    def __init__(self, name, env, x, y, grid, x_base, y_base, obstacles):
        self.name = name
        self.env = env
        self.x = x #posicao inicial
        self.y = y #posicao inicia
        self.grid = grid # representacao do terreno
        self.x_base = x_base 
        self.y_base = y_base
        self.resources_collected = 0
        self.obstacles = obstacles
        self.color = constantes.BLUE
        self.em_tempestade = False
        self.resources = grid
        self.process = env.process(self.run())

    def move_random(self):
        moves = [
                (0, 1),    # ↑
                (1, 1),    # ↗
                (1, 0),    # →
                (1, -1),   # ↘
                (0, -1),   # ↓
                (-1, -1),  # ↙
                (-1, 0),   # ←
                (-1, 1)    # ↖
            ]
        
        obstacle_positions = [(obstacle.x, obstacle.y) for obstacle in self.obstacles]

        random.shuffle(moves)  # Embaralha as direções para mais variedade
        for dx, dy in moves:
            new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
            new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))

            if (new_x, new_y) not in obstacle_positions:
                # Move o agente para a posição válida
                self.x, self.y = new_x, new_y
                return  # Sai do método após um movimento válido

    '''def verify_collected(self):
        # verificar recursos que foram coletados
        for resource in self.storage:
            if resource.type == "estrutura_antiga":
                SimpleAgent.base_comeback(self)
        return 0'''

    def collect_resource(self):
        for resource in self.grid:
                # Verificar se o recurso está na vizinhança
                if (
                    not resource.collected
                    and resource.type == "cristal"
                    and abs(resource.x - self.x) <= 1
                    and abs(resource.y - self.y) <= 1
                ):
                    # Move o agente até o recurso antes de coletar
                    self.x, self.y = resource.x, resource.y
                    resource.collected = True
                    self.resources_collected += resource.value
                    return True  # Recurso coletado
        return False  # Nenhum recurso coletado

    def return_to_base(self):
        while self.x != self.x_base or self.y != self.y_base:
            dx = self.x_base - self.x
            dy = self.y_base - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)
    
    def run(self):
        while True:
            if self.em_tempestade:
                yield from self.return_to_base()
                self.em_tempestade = False
            else:
                collected = self.collect_resource()
                if collected:
                    yield from self.return_to_base()  # Retorna à base para deixar o cristal
                else:
                    self.move_random()  # Caso contrário, continua se movendo
                yield self.env.timeout(1)

    def desenhar(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)

    # se mover pelo terreno (matriz bidimensional)
    # coletar recurso
    # 