import random

def Tempestade(env, agentes):
    yield env.timeout(random.randint(25, 50))  # Aguarda antes de começar

    print(" Tempestade iniciada!")

    for agente in agentes:
        agente.em_tempestade = True

    yield env.timeout(15)  # Duração da tempestade

    print("Tempestade terminou!")

    for agente in agentes:
        agente.em_tempestade = False