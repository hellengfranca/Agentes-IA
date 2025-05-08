import random

class Resource:
    def __init__(self, x, y, resource_type, required_agents):
        self.x = x
        self.y = y
        self.type = resource_type
        self.collected = False
        self.value = {"cristal": 10, "estrutura_antiga": 50, "metais": 20}.get(
            resource_type, 0
        )
        self.required_agents = required_agents
        self.color = {
            "cristal": (0, 255, 255),
            "estrutura_antiga": (139, 69, 19),
            "metais": (192, 192, 192),
        }.get(resource_type, (255, 255, 255))

    def copy(self):
        """Cria uma cópia independente deste recurso"""
        new_resource = Resource(self.x, self.y, self.type, self.required_agents)
        new_resource.collected = self.collected
        return new_resource