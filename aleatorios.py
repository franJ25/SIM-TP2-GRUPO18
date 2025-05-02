import random
import math


# Generar números aleatorios según la distribución uniforme
def generar_uniforme(n, a, b):
    if a >= b:
        raise ValueError("El parámetro 'a' debe ser menor que 'b'.")
    res = []
    for _ in range(n):
        rnd = random.random()
        uniforme = a + (b - a) * rnd
        res.append(round(uniforme, 4))
    return res


# Generar números aleatorios según la distribución exponencial negativa
def generar_exponencial(n, lambda_val):
    if lambda_val <= 0:
        raise ValueError("El parámetro 'lambda' debe ser positivo.")
    res = []
    for _ in range(n):
        rnd = random.random()
        exponencial = -math.log(1 - rnd) / lambda_val
        res.append(round(exponencial, 4))
    return res


# Generar números aleatorios según la distribución normal
def generar_normal(n, media, desv_est):
    if desv_est <= 0:
        raise ValueError("La desviación estándar 'sigma' debe ser positiva.")
    res = []
    for _ in range(n // 2):
        rnd1 = random.random()
        rnd2 = random.random()
        normal1 = (math.sqrt(-2 * math.log(rnd1)) * math.cos(2 * math.pi * rnd2)) * desv_est + media
        normal2 = (math.sqrt(-2 * math.log(rnd1)) * math.sin(2 * math.pi * rnd2)) * desv_est + media
        res.append(round(normal1, 4))
        res.append(round(normal2, 4))
    if n % 2 == 1:
        rnd1 = random.random()
        rnd2 = random.random()
        normal = (math.sqrt(-2 * math.log(rnd1)) * math.cos(2 * math.pi * rnd2)) * desv_est + media
        res.append(round(normal, 4))
    return res



