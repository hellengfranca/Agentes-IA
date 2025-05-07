import resources
import random
class SimpleAgent:
    def __init__(self, name, x, y, grid, x_base, y_base, obstacles):
        self.name = name
        self.x = x #posicao inicial
        self.y = y #posicao inicia
        self.grid = grid # representacao do terreno
        self.x_base = x_base 
        self.y_base = y_base
        self.resources_collected = []
        self.obstacles = obstacles
        self.in_storm = False

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

        dx, dy = random.choice(moves)
        new_x, new_y = dx, dy

        if (0 <= new_x < len(self.grid)) and (0 <= new_y < len(self.grid[0])):
            if (new_x, new_y) not in obstacle_positions: 
                self.x, self.y = new_x, new_y
                return 
            
        print(f"{self.name} nao pode se mover")

    '''def verify_collected(self):
        # verificar recursos que foram coletados
        for resource in self.storage:
            if resource.type == "estrutura_antiga":
                SimpleAgent.base_comeback(self)
        return 0'''

    def collect_resource(self, resource):
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

    def base_comeback(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            return 
        
    # se mover pelo terreno (matriz bidimensional)
    # coletar recurso
    # 