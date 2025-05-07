import pygame
import random
import simpy
import constantes

from resources import Resource
from agents.Agente_Baseado_Estados import AgenteBaseadoEmEstado
from Tempestade import Tempestade

def gerar_posicao_valida():
    while True:
        x = random.randint(0, 20 - 1)
        y = random.randint(0, 20 - 1)
        if not (0 <= x < 5 and 0 <= y < 5):  # evita a área da base
            return x, y

def main():
    pygame.init()
    screen = pygame.display.set_mode((20*20, 20*20))
    clock = pygame.time.Clock()
    env = simpy.Environment()

    # Obstáculos
    obstacles = [
        Resource(*gerar_posicao_valida(), "obstacle", 0) for _ in range(10)
    ]

    # Recursos
    resources = [
        Resource(*gerar_posicao_valida(), "cristal", 1) for _ in range(5)
    ] + [
        Resource(*gerar_posicao_valida(), "metais", 1) for _ in range(5)
    ] + [
        Resource(*gerar_posicao_valida(), "estrutura antiga", 2) for _ in range(3)
    ]

    # Agente baseado em estado (único agente)
    state_based_agent = AgenteBaseadoEmEstado(
        nome="Estado",
        ambiente=env,
        x=1,
        y=1,
        recursos=resources,
        base_x=0,
        base_y=0,
        obstaculos=obstacles,
        agente_cooperativo=None
    )

    agents = [state_based_agent]

    # Iniciar tempestade única
    env.process(Tempestade(env, agents))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.step()

        screen.fill(
            (222, 184, 135) if not any(agent.em_tempestade for agent in agents)
            else (255, 0, 0)
        )

        pygame.draw.rect(screen, (85, 107, 47), (0, 0, 100, 100))  # base

        for resource in resources:
            if not resource.collected:
                pygame.draw.circle(screen, resource.color, (resource.x * 20 + 10, resource.y * 20 + 10), 6)

        for obstacle in obstacles:
            pygame.draw.rect(screen, (0, 0, 0), (obstacle.x * 20, obstacle.y * 20, 20, 20))

        for agent in agents:
            agent.desenhar(screen)

        pygame.display.update()
        clock.tick(15)

    pygame.quit()

if __name__ == "__main__":
    main()