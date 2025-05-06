import random

class Resource:
    def __init__(self, x, y, resource_type, required_agents):
        self.x = x
        self.y = y
        self.type = resource_type
        self.collected = False
        self.value = {
            "cristal": 10, 
            "estrutura_antiga": 50, 
            "metal": 20
        }.get(resource_type, 0)
        self.agents = required_agents
        self.agents_value = {
            "cristal": 1,
            "estrutura_antiga": 2,
            "metal": 1,
        }.get(required_agents, 0)