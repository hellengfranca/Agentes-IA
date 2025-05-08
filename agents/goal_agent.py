import constantes
import random
import pygame

class GoalAgent():
    def __init__(self, name, env, x, y, grid, x_base, y_base, obstacles):
        self.name = name
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.x_base = x_base 
        self.y_base = y_base
        self.resources = grid
        self.resources_collected = 0
        self.resources_to_collect = [
            resource 
            for resource in grid 
            if not resource.collected and resource.type in ["cristal", "metal"]
        ]
        self.obstacles = obstacles
        self.color = constantes.PINK
        self.em_tempestade = False
        self.previous_position = None  
        self.carregando_recurso = False
        self.recurso_carregado = None
        self.process = env.process(self.run())

    def move_to_goal(self, resource):

        dx = resource.x - self.x
        dy = resource.y - self.y

        # Calcula distância Manhattan para priorização
        distance = abs(dx) + abs(dy)

        # Movimentos preferidos (direção do recurso)
        preferred_moves = []
        if dx != 0:
            new_x = self.x + (1 if dx > 0 else -1)
            if 0 <= new_x < constantes.GRID_WIDTH:
                preferred_moves.append((new_x, self.y))
        if dy != 0:
            new_y = self.y + (1 if dy > 0 else -1)
            if 0 <= new_y < constantes.GRID_HEIGHT:
                preferred_moves.append((self.x, new_y))

        # Adiciona movimentos diagonais como alternativas
        alter_moves = [
            (self.x + dx, self.y + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if (dx != 0 or dy != 0)  # Exclui a posição atual
        ]

        # Filtra movimentos válidos
        valid_moves = [
            move for move in (preferred_moves + alter_moves)
            if (0 <= move[0] < constantes.GRID_WIDTH and
                0 <= move[1] < constantes.GRID_HEIGHT and
                move not in [(o.x, o.y) for o in self.obstacles] and
                move != self.previous_position)
        ]

        if not valid_moves:
            # Se não houver movimentos válidos, tenta ignorar a posição anterior
            valid_moves = [
                move for move in (preferred_moves + alter_moves)
                if (0 <= move[0] < constantes.GRID_WIDTH and
                    0 <= move[1] < constantes.GRID_HEIGHT and
                    move not in [(o.x, o.y) for o in self.obstacles])
            ]

        if valid_moves:
            # Escolhe o movimento que mais reduz a distância ao recurso
            def distance_to_resource(move):
                return abs(move[0] - resource.x) + abs(move[1] - resource.y)

            # Ordena movimentos pela proximidade ao recurso
            valid_moves.sort(key=distance_to_resource)
            
            # Escolhe aleatoriamente entre os 3 melhores movimentos
            best_moves = valid_moves[:min(3, len(valid_moves))]
            chosen_move = random.choice(best_moves)
            
            self.previous_position = (self.x, self.y)
            self.x, self.y = chosen_move
        else:
            print(f"Agente {self.name} bloqueado em ({self.x}, {self.y})")

    def collect_resource(self):
        """Tenta coletar recurso na posição atual, se for coletável"""
        current_pos = (self.x, self.y)
        
        # Procura por recursos não coletados na posição atual
        for resource in self.resources_to_collect[:]:  # Usamos cópia da lista para poder remover itens
            if not resource.collected and (resource.x, resource.y) == current_pos:
                if resource.type in ["cristal", "metais"]:
                    resource.collected = True
                    self.carregando_recurso = True
                    self.recurso_carregado = resource
                    self.resources_collected += resource.value
                    self.resources_to_collect.remove(resource)
                    return True
        return False
        # Nenhum recurso coletado
            
    def return_to_base(self):
        while self.x != self.x_base or self.y != self.y_base:
            dx = self.x_base - self.x
            dy = self.y_base - self.y

            # Prioriza o movimento horizontal (x)
            next_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            next_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)

            # Lista de obstáculos como tuplas
            obstacle_positions = [(o.x, o.y) for o in self.obstacles]

            # Verifica se o próximo movimento está bloqueado
            if (next_x, self.y) in obstacle_positions:
                next_x = self.x  # Fixa a posição X se bloqueada

            if (self.x, next_y) in obstacle_positions:
                next_y = self.y  # Fixa a posição Y se bloqueada

            # Caso ambos estejam bloqueados, tenta desviar lateralmente
            if (next_x, next_y) in obstacle_positions:
                alternatives = [
                    (self.x + 1, self.y),  # Tenta mover para direita
                    (self.x - 1, self.y),  # Tenta mover para esquerda
                    (self.x, self.y + 1),  # Tenta mover para baixo
                    (self.x, self.y - 1),  # Tenta mover para cima
                ]
                # Filtra alternativas válidas
                alternatives = [
                    (alt_x, alt_y)
                    for alt_x, alt_y in alternatives
                    if 0 <= alt_x < constantes.GRID_WIDTH
                    and 0 <= alt_y < constantes.GRID_HEIGHT
                    and (alt_x, alt_y) not in obstacle_positions
                ]
                if alternatives:
                    next_x, next_y = random.choice(
                        alternatives
                    )  # Escolhe uma posição válida

            # Atualiza a posição do agente
            self.x, self.y = next_x, next_y

            # Aguarda o próximo passo no ambiente
            yield self.env.timeout(1)

    def run(self):
        while True:
            # 1. Prioridade: Tempestade - retornar à base
            if self.em_tempestade:
                yield from self.return_to_base()
                self.carregando_recurso = False
                self.recurso_carregado = None
                yield self.env.timeout(1)
                continue
            
            # 2. Se está carregando recurso, retorna à base
            if self.carregando_recurso:
                yield from self.return_to_base()
                self.carregando_recurso = False
                self.recurso_carregado = None
                yield self.env.timeout(1)
                continue
            
            # 3. Atualiza lista de recursos disponíveis
            self.resources_to_collect = [
                r for r in self.grid 
                if not r.collected and r.type in ["cristal", "metais"]
            ]
            
            # 4. Se não há recursos, espera
            if not self.resources_to_collect:
                yield self.env.timeout(1)
                continue
            
            # 5. Busca pelo recurso mais próximo
            closest = min(
                self.resources_to_collect,
                key=lambda r: abs(self.x - r.x) + abs(self.y - r.y))
            
            # 6. Tenta coletar se já está no recurso
            if (self.x, self.y) == (closest.x, closest.y):
                if not self.collect_resource():
                    # Se não conseguiu coletar, remove o recurso da lista
                    self.resources_to_collect.remove(closest)
                yield self.env.timeout(1)
                continue
            
            # 7. Move-se em direção ao recurso
            self.move_to_goal(closest)
            yield self.env.timeout(1)

    def desenhar(self, screen):
        """Desenha o agente na tela."""
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
