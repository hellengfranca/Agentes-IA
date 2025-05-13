import pygame
import random
import simpy
import constantes

from resources import Resource
from Tempestade import Tempestade
from agents.Agente_Baseado_Estados import AgenteBaseadoEmEstado
from agents.Agente_Coperativo import AgenteCoperativo
from agents.AgenteBDI import AgenteBDI
from agents.goal_agent import GoalAgent
from agents.simple_agent import SimpleAgent

def gerar_posicao_valida():
    while True:
        x = random.randint(0, constantes.GRID_WIDTH - 1)
        y = random.randint(0, constantes.GRID_HEIGHT - 1)
        if not (0 <= x < 5 and 0 <= y < 5):
            return x, y

def mostrar_tela_inicial(tela):
    fonte = pygame.font.SysFont("times", 36)
    titulo = fonte.render("Trabalho Agentes", True, (255, 255, 255))
    botao_rect = pygame.Rect(constantes.WINDOW_WIDTH // 2 - 100, constantes.WINDOW_HEIGHT // 2 - 25, 200, 50)
    texto = fonte.render("Iniciar ", True, (255, 255, 255))

    esperando = True
    while esperando:
        tela.fill((100, 100, 100))

        # botão com borda arredondada
        pygame.draw.rect(tela, (70, 130, 180), botao_rect, border_radius=10)

        # título no topo
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 100))

        # texto dentro do botão
        tela.blit(texto, (constantes.WINDOW_WIDTH // 2 - texto.get_width() // 2, constantes.WINDOW_HEIGHT // 2 - texto.get_height() // 2))
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN and botao_rect.collidepoint(evento.pos):
                esperando = False

def mostrar_tela_resultado(tela, agentes):
    fonte = pygame.font.SysFont("arial", 28)
    titulo = fonte.render("Resultados da Simulação", True, (255, 255, 255))
    botao_rect = pygame.Rect(constantes.WINDOW_WIDTH // 2 - 150, constantes.WINDOW_HEIGHT - 100, 300, 50)
    texto_botao = fonte.render("Refazer Simulação", True, (255, 255, 255))

    esperando = True
    while esperando:
        tela.fill((100, 100, 100))
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 40))

        for i, agente in enumerate(agentes):
            nome = agente.nome
            pontos = getattr(agente, 'pontuacao', 0)  # Usa .pontuacao se existir; senão 0
            resultado = fonte.render(f"{nome}: {pontos} pontos", True, (255, 255, 255))
            tela.blit(resultado, (60, 100 + i * 40))

        pygame.draw.rect(tela, (70, 130, 180), botao_rect, border_radius=10)
        tela.blit(texto_botao, (constantes.WINDOW_WIDTH // 2 - texto_botao.get_width() // 2, botao_rect.y + 10))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN and botao_rect.collidepoint(evento.pos):
                main()
                return
def main():
    pygame.init()
    tela = pygame.display.set_mode((constantes.WINDOW_WIDTH, constantes.WINDOW_HEIGHT))
    relogio = pygame.time.Clock()
    ambiente = simpy.Environment()
    tempestade_ocorreu = False
    tempo_apos_tempestade = 0
    mostrar_tela_inicial(tela)

    # Obstáculos
    obstaculos = [Resource(*gerar_posicao_valida(), "obstacle", 0) for _ in range(10)]

    # Recursos
    recursos = (
        [Resource(*gerar_posicao_valida(), "cristal", 1) for _ in range(10)] +
        [Resource(*gerar_posicao_valida(), "metais", 1) for _ in range(10)] +
        [Resource(*gerar_posicao_valida(), "estrutura antiga", 2) for _ in range(7)]
    )

    # Criação dos agentes
    agente_bdi = AgenteBDI("BDI", ambiente, 2, 1, recursos, 0, 0, obstaculos)

    agente_coop = AgenteCoperativo(
        "Cooperativo",
        ambiente,
        1, 1,
        recursos,
        0, 0,
        obstaculos,
        todos_os_agentes=None,  # atualizado depois
        agente_bdi=agente_bdi
    )

    agente_estado = AgenteBaseadoEmEstado(
        "Estado",
        ambiente,
        1, 2,
        recursos,
        0, 0,
        obstaculos,
        agente_coop,
        agente_bdi
    )

    agente_goal = GoalAgent("Objetivo", ambiente, 2, 2, recursos, 0, 0, obstaculos, agente_coop, agente_bdi)
    agente_simple = SimpleAgent("Simples", ambiente, 3, 1, recursos, 0, 0, obstaculos)

    # Lista final de agentes
    agentes = [agente_estado, agente_coop, agente_bdi, agente_goal, agente_simple]

    # Compartilhar lista completa com os agentes que precisam
    agente_coop.todos_os_agentes = agentes
    agente_bdi.todos_os_agentes = agentes  # caso o BDI precise conhecer os outros

    ambiente.process(Tempestade(ambiente, agentes))

    passos = 0
    rodando = True
    TEMPO_SIMULACAO = 60

    while rodando and passos < constantes.FPS * TEMPO_SIMULACAO:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        ambiente.step()
        (85, 107, 47)
        
        tela.fill(
            constantes.EARTH if not any(a.em_tempestade for a in agentes)
            else constantes.RED
        )

        pygame.draw.rect(tela, constantes.MOSS_GREEN, (0, 0, 80, 80))

        for recurso in recursos:
            if not recurso.collected:
                pygame.draw.circle(tela, recurso.color, (recurso.x * 20 + 10, recurso.y * 20 + 10), 6)

        for obstaculo in obstaculos:
            pygame.draw.rect(tela, constantes.BLACK, (obstaculo.x * 20, obstaculo.y * 20, 20, 20))

        for agente in agentes:
            agente.desenhar(tela)

        if any(a.em_tempestade for a in agentes):
            tempestade_ocorreu = True

        elif tempestade_ocorreu:
            tempo_apos_tempestade += 1
            if tempo_apos_tempestade > constantes.FPS * 0:  
                mostrar_tela_resultado(tela, agentes)
                return                        

        pygame.display.update()
        passos += 1
        relogio.tick(constantes.FPS)

    mostrar_tela_resultado(tela, agentes)
   

if __name__ == "__main__":
    main()

