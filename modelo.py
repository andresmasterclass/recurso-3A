"""Modelo de la Situación 3A (rendimiento de una aplicación web).

Funciones puras (sin Streamlit) para poder probarlas por separado.
x = miles de usuarios, t = semanas, n = número de servidores.
"""
import math

CAPACIDAD = 20          # miles de usuarios que soporta la infraestructura
MAX_SERVIDORES = 20     # espacio del centro de datos


# ---- Tiempo de respuesta (segundos) -------------------------------------
def T(x):            # versión original
    return (5 * x + 40) / (x - 4)

def T_der(x):        # T'(x) = -60/(x-4)^2
    return -60 / (x - 4) ** 2

def Ts(x):           # versión nueva, ya simplificada: (x+4)/x  (T*(4)=2)
    return (x + 4) / x

def Ts_der(x):       # T*'(x) = -4/x^2
    return -4 / x ** 2


# ---- Usuarios en el tiempo (miles) --------------------------------------
def x_t(t):
    return 20 / (1 + 9 * math.exp(-0.4 * t))

def x_der(t):        # ritmo de crecimiento (miles de usuarios por semana)
    u = math.exp(-0.4 * t)
    return 72 * u / (1 + 9 * u) ** 2

def x_der2(t):
    u = math.exp(-0.4 * t)
    return -28.8 * u * (1 - 9 * u) / (1 + 9 * u) ** 3

T_INFLEXION = math.log(9) / 0.4      # ≈ 5,49 semanas (x = 10 mil)


# ---- Costo de los servidores (miles de pesos al mes) --------------------
def costo(n, k):
    return 120 * n + (4800 + 200 * k) / n

def n_optimo_continuo(k):
    return math.sqrt((4800 + 200 * k) / 120)

def mejor_n(k):
    """Entero entre 1 y 20 con menor costo (se comparan los vecinos de n*)."""
    ns = n_optimo_continuo(k)
    candidatos = [n for n in (math.floor(ns), math.ceil(ns))
                  if 1 <= n <= MAX_SERVIDORES]
    if not candidatos:
        candidatos = [MAX_SERVIDORES]
    return min(candidatos, key=lambda n: costo(n, k))
