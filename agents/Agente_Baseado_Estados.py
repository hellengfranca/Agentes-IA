
import random
import pygame

class AgenteBaseadoEmEstado:
    def __init__(self, nome, ambiente, x, y, recursos, base_x, base_y, obstaculos, agente_cooperativo):
        self.nome = nome                            
        self.ambiente = ambiente                    
        self.x = x                                  
        self.y = y                                  
        self.base_x = base_x                        
        self.base_y = base_y                        
        self.recursos = recursos                    
        self.obstaculos = obstaculos                
        self.posicoes_exploradas = set()            
        self.carregando_recurso = False             
        self.recurso_carregado = None               
        self.recursos_entregues = []                
        self.conhecimento_compartilhado = {}        
        self.agente_cooperativo = agente_cooperativo  
        self.em_tempestade = False                  
        self.cor = (0, 255, 0)              
        self.processo = ambiente.process(self.run())
        

        # Inicia o processo comportamental do agente no ambiente de simulação
        
    def coletar_recurso(self):
        """Tenta coletar recurso pequeno/médio ou acionar ajuda para estrutura antiga."""
        vizinhos = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        ]

        for recurso in self.recursos:
            if not recurso.collected and (recurso.x, recurso.y) in vizinhos:
                
                # Recursos pequenos ou médios (cristal, metais)
                if recurso.type in ["cristal", "metais"]:
                    if not self.carregando_recurso:
                        recurso.collected = True
                        self.carregando_recurso = True
                        self.recurso_carregado = recurso
                        self.conhecimento_compartilhado[(recurso.x, recurso.y)] = "coletado"
                        self.x, self.y = recurso.x, recurso.y
                        return True  # Recurso coletado

                # Estrutura grande
                elif recurso.type == "estrutura antiga":
                    if not self.carregando_recurso:
                        self.conhecimento_compartilhado[(recurso.x, recurso.y)] = "estrutura antiga"
                        self.agente_cooperativo.receber_chamada(recurso)
                        self.recurso_carregado = recurso
                        # Não marca como coletado ainda — espera ajuda
                        return False  # Espera pelo cooperativo

        return False  # Nenhum recurso coletado

    def retornar_para_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            delta_x = self.base_x - self.x
            delta_y = self.base_y - self.y

            novo_x = self.x + (1 if delta_x > 0 else -1 if delta_x < 0 else 0)
            novo_y = self.y + (1 if delta_y > 0 else -1 if delta_y < 0 else 0)

            if (novo_x, novo_y) not in [(obstaculo.x, obstaculo.y) for obstaculo in self.obstaculos]:
                self.x, self.y = novo_x, novo_y
            else:
                self.mover_explorando()  # Movimento alternativo se bloqueado

            yield self.ambiente.timeout(1)

    def mover_explorando(self):
        """Move o agente para uma área não explorada ou tenta escapar de situações bloqueadas."""
        vizinhos = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
        ]

        movimentos_validos = [
            (nx, ny)
            for nx, ny in vizinhos
            if 0 <= nx < 20
            and 0 <= ny < 20
            and (nx, ny) not in self.posicoes_exploradas
            and (nx, ny) not in [(obstaculo.x, obstaculo.y) for obstaculo in self.obstaculos]
        ]

        if movimentos_validos:
            novo_x, novo_y = random.choice(movimentos_validos)
            self.x, self.y = novo_x, novo_y
            self.posicoes_exploradas.add((novo_x, novo_y))
        else:
            movimentos_alternativos = [
                (nx, ny)
                for nx, ny in vizinhos
                if 0 <= nx < 20
                and 0 <= ny < 20
                and (nx, ny) not in [(obstaculo.x, obstaculo.y) for obstaculo in self.obstaculos]
            ]
            if movimentos_alternativos:
                self.x, self.y = random.choice(movimentos_alternativos)


    def run(self):
        while True:
            if self.em_tempestade:
                yield from self.retornar_para_base()
                self.em_tempestade = False

            elif self.carregando_recurso:
                yield from self.retornar_para_base()
                self.carregando_recurso = False
                if self.recurso_carregado:
                    self.recursos_entregues.append(self.recurso_carregado)
                    self.recurso_carregado = None

            elif self.recurso_carregado and self.recurso_carregado.tipo == "estrutura antiga":
                # Espera enquanto a estrutura ainda estiver no ambiente
                if self.recurso_carregado in self.recursos:
                    yield self.ambiente.timeout(1)
                else:
                    # Estrutura foi coletada pelo agente cooperativo
                    self.recurso_carregado = None

            else:
                self.mover_explorando()
                if self.coletar_recurso():
                    yield from self.retornar_para_base()
                    self.carregando_recurso = False
                    if self.recurso_carregado:
                        self.recursos_entregues.append(self.recurso_carregado)
                        self.recurso_carregado = None
                else:
                    self.mover_explorando()

            yield self.ambiente.timeout(1)

    def desenhar(self, tela):
        """Desenha o agente na tela."""
        pygame.draw.circle(
            tela,
            self.cor,
            (self.x * 20 + 10, self.y * 20 + 10),
            8
        )
