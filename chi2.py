from scipy.stats import chi2, norm
import math


# Prueba chi cuadrado para distribución exponencial
def chi2_exponencial(frecuencias_observadas, limites, n, lambda_val, alpha):
    print("frecs obs: ", frecuencias_observadas)
    print("limis:", limites)
    k = len(limites) - 1
    frecuencias_esperadas = []
    for i in range(k):
        a, b = limites[i], limites[i+1]
        probabilidad = (1 - math.e ** (-lambda_val * b)) - (1 - math.e ** (-lambda_val * a))
        fe = n * probabilidad
        frecuencias_esperadas.append(fe)
    print("frecs esp:", frecuencias_esperadas)
    nuevos_fe, nuevos_fo, nuevos_limites = agrupar_frecuencias(frecuencias_observadas, frecuencias_esperadas, limites)
    print("Nuevas fe:", nuevos_fe)
    print("Nuevas fo:", nuevos_fo)
    print("Nuevos límites:", nuevos_limites)
    estadistico_de_prueba = 0
    for fo, fe in zip(nuevos_fo, nuevos_fe):
        estadistico_de_prueba += ((fo - fe) ** 2) / fe
    print("chi calculado: ", estadistico_de_prueba)
    grados_de_libertad = k - 1 - 1
    chi_tabla = chi2.ppf(1 - alpha, grados_de_libertad)
    print("chi tabla: ", chi_tabla)
    res = f"Resultado:\n\tChi calculado: {round(estadistico_de_prueba, 2)}\n\tChi de tabla: {round(chi_tabla, 2)}\n"
    if estadistico_de_prueba > chi_tabla:
        print("Hipótesis nula rechazada")
        return res + "\nConclusión: Hipótesis Nula rechazada"
    else:
        print("No hay suficientes pruebas para rechazar la hipótesis nula")
        return res + "\nConclusión: No hay suficientes pruebas para rechazar la hipótesis nula"


# Prueba chi cuadrado para distribución normal
def chi2_normal(frecuencias_observadas, limites, n, media, desv_est, alpha):
    print("frecs obs: ", frecuencias_observadas)
    print("limis:", limites)
    k = len(limites) - 1
    frecuencias_esperadas = []
    for i in range(k):
        a, b = limites[i], limites[i+1]
        probabilidad = norm.cdf(b, media, desv_est) - norm.cdf(a, media, desv_est)
        fe = n * probabilidad
        frecuencias_esperadas.append(fe)
    print("frecs esp:", frecuencias_esperadas)
    nuevos_fe, nuevos_fo, nuevos_limites = agrupar_frecuencias(frecuencias_observadas, frecuencias_esperadas, limites)
    print("Nuevas fe:", nuevos_fe)
    print("Nuevas fo:", nuevos_fo)
    print("Nuevos límites:", nuevos_limites)

    estadistico_de_prueba = 0
    for fo, fe in zip(nuevos_fo, nuevos_fe):
        estadistico_de_prueba += ((fo - fe) ** 2) / fe
    print("chi calculado: ", estadistico_de_prueba)
    grados_de_libertad = k - 1 - 2
    chi_tabla = chi2.ppf(1 - alpha, grados_de_libertad)
    print("chi tabla: ", chi_tabla)
    res = f"Resultado:\n\tChi calculado: {round(estadistico_de_prueba, 2)}\n\tChi de tabla: {round(chi_tabla, 2)}\n"
    if estadistico_de_prueba > chi_tabla:
        print("Hipótesis nula rechazada")
        return res + "\nConclusión: Hipótesis Nula rechazada"
    else:
        print("No hay suficientes pruebas para rechazar la hipótesis nula")
        return res + "\nConclusión: No hay suficientes pruebas para rechazar la hipótesis nula"


# Prueba chi cuadrado para distribución uniforme
def chi2_uniforme(frecuencias_observadas, limites, n, alpha):
    print("frecs obs: ", frecuencias_observadas)
    print("limis:", limites)
    k = len(limites) - 1
    frecuencias_esperadas = [n / k] * k
    print("frecs esp:", frecuencias_esperadas)
    nuevos_fe, nuevos_fo, nuevos_limites = agrupar_frecuencias(frecuencias_observadas, frecuencias_esperadas, limites)
    print("Nuevas fe:", nuevos_fe)
    print("Nuevas fo:", nuevos_fo)
    print("Nuevos límites:", nuevos_limites)
    estadistico_de_prueba = 0
    for fo, fe in zip(nuevos_fo, nuevos_fe):
        estadistico_de_prueba += ((fo - fe) ** 2) / fe
    print("chi calculado: ", estadistico_de_prueba)
    grados_de_libertad = k - 1
    chi_tabla = chi2.ppf(1 - alpha, grados_de_libertad)
    print("chi tabla: ", chi_tabla)
    res = f"Resultado:\n\tChi calculado: {round(estadistico_de_prueba, 2)}\n\tChi de tabla: {round(chi_tabla, 2)}\n"
    if estadistico_de_prueba > chi_tabla:
        print("Hipótesis nula rechazada")
        return res + "\nConclusión: Hipótesis Nula rechazada"
    else:
        print("No hay suficientes pruebas para rechazar la hipótesis nula")
        return res + "\nConclusión: No hay suficientes pruebas para rechazar la hipótesis nula"


def agrupar_frecuencias(frecuencias_observadas, frecuencias_esperadas, limites):
    nuevos_fo = []
    nuevos_fe = []
    nuevos_limites = []
    i = 0
    while i < len(frecuencias_esperadas):
        fe_actual = frecuencias_esperadas[i]
        fo_actual = frecuencias_observadas[i]
        a = limites[i]
        b = limites[i+1]
        while fe_actual < 5 and i + 1 < len(frecuencias_esperadas):
            i += 1
            fe_actual += frecuencias_esperadas[i]
            fo_actual += frecuencias_observadas[i]
            b = limites[i+1]
        nuevos_fe.append(fe_actual)
        nuevos_fo.append(fo_actual)
        nuevos_limites.append((a, b))
        i += 1

    # Agrupar hacia atrás si el último sigue teniendo fe < 5
    while len(nuevos_fe) > 1 and nuevos_fe[-1] < 5:
        nuevos_fe[-2] += nuevos_fe[-1]
        nuevos_fo[-2] += nuevos_fo[-1]
        nuevos_limites[-2] = (nuevos_limites[-2][0], nuevos_limites[-1][1])
        nuevos_fe.pop()
        nuevos_fo.pop()
        nuevos_limites.pop()
    return nuevos_fe, nuevos_fo, nuevos_limites

