"""Recurso interactivo – Situación 3A: rendimiento de una aplicación web.

Ejecutar:
    pip install streamlit sympy matplotlib numpy
    streamlit run app.py
"""
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import sympy as sp

import modelo as m

st.set_page_config(page_title="Rendimiento de una aplicación web", layout="wide")

# ------------------------------------------------------------------ datos
st.title("Rendimiento de una aplicación web – Situación 3A")
st.caption("Cálculo diferencial 2026-II · Equipo B (Análisis). "
           "x en miles de usuarios, t en semanas, tiempos en segundos. "
           "Todo es un modelo teórico: debe validarse con pruebas de carga.")

with st.sidebar:
    st.header("Datos que puede cambiar")
    k = st.slider("k (parámetro de penalidades)", 1, 100, 5)
    x0 = st.slider("Usuarios conectados x (miles)", 4.1, 20.0, 6.0, 0.1)
    t0 = st.slider("Semana t", 0.0, 15.0, 4.0, 0.5)
    n0 = st.slider("Servidores n", 1, 20, 7)
    st.markdown("---")
    st.markdown("**Umbral de la promesa comercial:** 4 s")
    umbral = st.number_input("Umbral (s)", 1.0, 10.0, 4.0, 0.5)

# ------------------------------------------------- derivadas con SymPy
xs, ts, ns, ks = sp.symbols("x t n k", positive=True)
T_sym = (5 * xs + 40) / (xs - 4)
Ts_sym = sp.cancel((xs**2 - 16) / (xs**2 - 4 * xs))      # (x+4)/x
X_sym = 20 / (1 + 9 * sp.exp(-sp.Rational(2, 5) * ts))
C_sym = 120 * ns + (4800 + 200 * ks) / ns

dT = sp.diff(T_sym, xs)
dTs = sp.diff(Ts_sym, xs)
dX = sp.diff(X_sym, ts)
d2X = sp.diff(X_sym, ts, 2)
dC = sp.diff(C_sym, ns)
n_crit = sp.solve(sp.Eq(dC, 0), ns)

f_dT = sp.lambdify(xs, dT, "numpy")
f_dTs = sp.lambdify(xs, dTs, "numpy")
f_dX = sp.lambdify(ts, dX, "numpy")

# --------------------------------------------------------- indicadores
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"T(x) original con x = {x0:.1f}", f"{m.T(x0):.2f} s",
            f"{float(f_dT(x0)):.2f} s por cada mil usuarios")
col2.metric(f"T*(x) nueva con x = {x0:.1f}", f"{m.Ts(x0):.3f} s",
            f"{float(f_dTs(x0)):.3f} s por cada mil usuarios")
xt = m.x_t(t0)
col3.metric(f"Usuarios en la semana {t0:.1f}", f"{xt:.2f} mil",
            f"{float(f_dX(t0)):.2f} mil por semana")
dTdt = m.Ts_der(xt) * m.x_der(t0)
col4.metric("Cambio de T* en esa semana", f"{dTdt:.3f} s/semana")

tab1, tab2, tab3, tab4 = st.tabs(
    ["1. Original vs nueva", "2. Usuarios en el tiempo",
     "3. Servidores y costo", "4. Decisión"])

# ---------------------------------------------------------------- tab 1
with tab1:
    x = np.linspace(4.05, 20, 600)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(x, m.T(x), label="T(x) original", color="#B84A14")
    ax[0].plot(x, m.Ts(x), label="T*(x) nueva", color="#15213B")
    ax[0].axhline(umbral, ls="--", color="gray", label=f"promesa ({umbral:g} s)")
    ax[0].axvline(4, ls=":", color="#B84A14")
    ax[0].axhline(5, ls=":", color="#B84A14")
    ax[0].plot([x0], [m.T(x0)], "o", color="#B84A14")
    ax[0].plot([x0], [m.Ts(x0)], "o", color="#15213B")
    ax[0].set_ylim(0, 60)
    ax[0].set_xlabel("Usuarios x (miles)")
    ax[0].set_ylabel("Tiempo de respuesta (s)")
    ax[0].set_title("Modelo: tiempo de respuesta")
    ax[0].legend()
    ax[1].plot(x, f_dT(x), label="T'(x)", color="#B84A14")
    ax[1].plot(x, f_dTs(x), label="T*'(x)", color="#15213B")
    ax[1].set_ylim(-20, 1)
    ax[1].set_xlabel("Usuarios x (miles)")
    ax[1].set_ylabel("Ritmo de cambio (s por cada mil usuarios)")
    ax[1].set_title("Derivada: qué tan rápido cambia")
    ax[1].legend()
    st.pyplot(fig)
    st.markdown(
        "- La original tiene asíntota vertical en x = 4 y nunca baja de 5 s.\n"
        "- La nueva se mantiene entre 1 s y 2 s para x > 4.\n"
        "- En x = 4 la nueva tiene un hueco: se define T*(4) = 2 s "
        "(T*'(4) = −0,25).")

# ---------------------------------------------------------------- tab 2
with tab2:
    t = np.linspace(0, 15, 400)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(t, 20 / (1 + 9 * np.exp(-0.4 * t)), color="#15213B")
    ax[0].axhline(m.CAPACIDAD, ls="--", color="gray", label="capacidad (20 mil)")
    ax[0].plot([m.T_INFLEXION], [10], "o", color="#B84A14",
               label="punto de inflexión")
    ax[0].plot([t0], [xt], "s", color="#15213B")
    ax[0].set_xlabel("Semana t")
    ax[0].set_ylabel("Usuarios x(t) (miles)")
    ax[0].set_title("Crecimiento de usuarios")
    ax[0].legend()
    ax[1].plot(t, f_dX(t), color="#B84A14")
    ax[1].axvline(m.T_INFLEXION, ls="--", color="gray")
    ax[1].set_xlabel("Semana t")
    ax[1].set_ylabel("x'(t) (miles de usuarios por semana)")
    ax[1].set_title("Ritmo de crecimiento (máximo en la inflexión)")
    st.pyplot(fig)
    st.markdown(
        f"- Punto de inflexión: t = ln 9 / 0,4 ≈ **{m.T_INFLEXION:.2f} semanas**, "
        f"con x = 10 mil usuarios y ritmo máximo de {m.x_der(m.T_INFLEXION):.1f} mil por semana.\n"
        "- Los usuarios tienden a 20 mil, que es la capacidad de la infraestructura.")

# ---------------------------------------------------------------- tab 3
with tab3:
    n = np.arange(1, m.MAX_SERVIDORES + 1)
    costos = np.array([m.costo(i, k) for i in n])
    mejor = m.mejor_n(k)
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(n, 120 * n, label="servidores (120 por unidad)", color="#9FB0CC")
    ax.bar(n, (4800 + 200 * k) / n, bottom=120 * n,
           label="penalidades", color="#F0A070")
    ax.plot(n, costos, "o-", color="#15213B", label="costo total C(n)")
    ax.plot([mejor], [m.costo(mejor, k)], "*", ms=18, color="#B84A14",
            label=f"mínimo entero: n = {mejor}")
    ax.set_xticks(n)
    ax.set_xlabel("Servidores n")
    ax.set_ylabel("Costo mensual (miles de pesos)")
    ax.set_title(f"Costo mensual con k = {k}")
    ax.legend()
    st.pyplot(fig)
    st.latex("C(n)=120n+\\frac{4800+200k}{n}")
    st.latex("n^{*}=\\sqrt{40+\\tfrac{5k}{3}}=" + sp.latex(n_crit[0]) +
             f"\\approx {m.n_optimo_continuo(k):.2f}")
    st.markdown(
        f"Con n = {n0} servidores el costo es **{m.costo(n0, k):,.1f}** mil pesos al mes; "
        f"el mejor entero es **n = {mejor}** (**{m.costo(mejor, k):,.1f}** mil pesos).")

# ---------------------------------------------------------------- tab 4
with tab4:
    mejor = m.mejor_n(k)
    st.subheader("Recomendación (según el modelo)")
    st.success(
        f"1. **Versión:** publicar la nueva. Responde entre 1 y 2 s para x > 4 "
        f"(umbral de {umbral:g} s), mientras la original nunca baja de 5 s.\n\n"
        f"2. **Servidores:** contratar **{mejor}** (costo mínimo de "
        f"{m.costo(mejor, k):,.1f} mil pesos al mes con k = {k}).\n\n"
        f"3. **Refuerzo:** dejar la infraestructura lista antes de la semana "
        f"**{m.T_INFLEXION:.1f}**, cuando los usuarios crecen más rápido.\n\n"
        "4. **Condición:** validar estos resultados con pruebas de carga reales.")
    if m.Ts(x0) < umbral < m.T(x0):
        st.info("Con estos datos la versión nueva cumple el umbral y la original no.")
    elif m.T(x0) < umbral:
        st.info("Con estos datos ambas versiones cumplen el umbral.")

# --------------------------------------------------- verificación
with st.expander("Fórmulas y verificación de las derivadas"):
    st.latex("T(x)=\\frac{5x+40}{x-4}\\quad T'(x)=" + sp.latex(sp.simplify(dT)))
    st.latex("T^{*}(x)=\\frac{x^2-16}{x^2-4x}=" + sp.latex(Ts_sym) +
             "\\quad T^{*\\prime}(x)=" + sp.latex(sp.simplify(dTs)))
    st.latex("x(t)=\\frac{20}{1+9e^{-0.4t}}\\quad x'(t)="
             "\\frac{72e^{-0.4t}}{(1+9e^{-0.4t})^2}")
    h = 1e-6
    num = (m.T(x0 + h) - m.T(x0 - h)) / (2 * h)
    st.write(f"En x = {x0:.1f}: derivada simbólica {float(f_dT(x0)):.6f} · "
             f"derivada numérica {num:.6f}")
