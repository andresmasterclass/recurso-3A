"""Monitor 3A – recurso interactivo de la Situación 3A (rendimiento de una aplicación web).

Ejecutar:
    pip install -r requirements.txt
    streamlit run app.py
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import sympy as sp
from plotly.subplots import make_subplots

import modelo as m

st.set_page_config(page_title="Monitor 3A · Rendimiento web", page_icon="📈",
                   layout="wide")

# ----------------------------------------------------------------- paleta
ORIG = "#C8553D"      # versión original (terracota)
NUEVA = "#0E7C66"     # versión nueva (verde petróleo)
USU = "#3D5A80"       # usuarios (azul pizarra)
COSTO = "#E0A458"     # costos (ámbar)
TINTA = "#1F2A37"
REJILLA = "#DDD5C7"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, label, p, li { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }
section[data-testid="stSidebar"] { background: #1F2A37; }
section[data-testid="stSidebar"] * { color: #F5F1EA !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] * { color: #1F2A37 !important; }
section[data-testid="stSidebar"] input { color: #1F2A37 !important; }
.banda { background: linear-gradient(100deg, #1F2A37 0%, #24435A 60%, #0E7C66 100%);
         border-radius: 18px; padding: 26px 30px; color: #F5F1EA; margin-bottom: 18px; }
.banda h1 { color: #F5F1EA; margin: 0; font-size: 2.1rem; }
.banda p { color: #D9E4E1; margin: 6px 0 0 0; font-size: 0.98rem; }
.chip { display: inline-block; background: rgba(245,241,234,0.14); border: 1px solid rgba(245,241,234,0.35);
        border-radius: 999px; padding: 3px 12px; font-size: 0.78rem; margin-right: 6px; margin-bottom: 10px;
        font-family: 'IBM Plex Mono', monospace; }
.rejilla { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; }
.tarjeta { background: #FFFDF9; border: 1px solid #E4DCCD; border-radius: 16px; padding: 16px 18px;
           border-top: 6px solid var(--c); }
.tarjeta .t { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: #6B6455; }
.tarjeta .v { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; color: var(--c); line-height: 1.15; margin-top: 4px; }
.tarjeta .s { font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; color: #3F3A31; margin-top: 4px; }
.sello { display: inline-block; margin-top: 8px; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.ok { background: #DCEFE9; color: #0B5E4E; } .mal { background: #F6DED8; color: #8E3524; } .neutro { background: #E7E1D5; color: #4A4436; }
.veredicto { background: #FFFDF9; border: 1px solid #E4DCCD; border-left: 8px solid var(--c); border-radius: 14px;
             padding: 16px 18px; margin-bottom: 12px; }
.veredicto h4 { margin: 0 0 6px 0; color: var(--c); }
.nota { font-size: 0.85rem; color: #6B6455; }
.pie { text-align: center; color: #6B6455; font-size: 0.8rem; margin-top: 28px; }
</style>
""", unsafe_allow_html=True)


def es(v, d=2):
    """Número con formato colombiano: coma decimal y punto de miles."""
    s = f"{v:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def tarjeta(titulo, valor, sub, color, sello=None, clase="neutro"):
    html = (f'<div class="tarjeta" style="--c:{color}"><div class="t">{titulo}</div>'
            f'<div class="v">{valor}</div><div class="s">{sub}</div>')
    if sello:
        html += f'<span class="sello {clase}">{sello}</span>'
    return html + "</div>"


def estilo(fig, alto=420):
    fig.update_layout(
        height=alto, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFDF9",
        font=dict(family="IBM Plex Sans, sans-serif", color=TINTA, size=13),
        margin=dict(l=10, r=10, t=50, b=40), hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.16, x=0))
    fig.update_xaxes(gridcolor=REJILLA, zeroline=False, showline=True, linecolor="#B9AE99")
    fig.update_yaxes(gridcolor=REJILLA, zeroline=False, showline=True, linecolor="#B9AE99")
    return fig


# --------------------------------------------------- escenarios "¿qué pasa si…?"
ESCENARIOS = {
    "Caso del reporte (x = 6 mil, semana 4, k = 5)":
        dict(k=5, x=6.0, t=4.0, n=7, sync=False),
    "Pico de crecimiento (semana 5,5)":
        dict(k=5, x=10.0, t=5.5, n=7, sync=True),
    "Penalidades altas (k = 40)":
        dict(k=40, x=6.0, t=4.0, n=m.mejor_n(40), sync=False),
    "Infraestructura casi llena (19 mil usuarios)":
        dict(k=5, x=19.0, t=12.0, n=7, sync=False),
}
INICIAL = ESCENARIOS["Caso del reporte (x = 6 mil, semana 4, k = 5)"]
for clave, valor in {**INICIAL, "umbral": 4.0}.items():
    st.session_state.setdefault(clave, valor)


def aplicar_escenario():
    elegido = st.session_state["escenario"]
    if elegido in ESCENARIOS:
        st.session_state.update(ESCENARIOS[elegido])


# ------------------------------------------------------------- panel lateral
with st.sidebar:
    st.markdown("### 🎛️ Panel de control")
    st.selectbox("Escenario rápido", ["Personalizado"] + list(ESCENARIOS),
                 key="escenario", on_change=aplicar_escenario,
                 help="Carga valores típicos para responder preguntas «¿qué pasa si…?».")
    st.markdown("**Negocio**")
    k = st.slider("k · parámetro de penalidades", 1, 100, key="k")
    umbral = st.slider("Promesa comercial (s)", 1.0, 10.0, step=0.5, key="umbral")
    st.markdown("**Carga**")
    t0 = st.slider("Semana t desde el lanzamiento", 0.0, 15.0, step=0.5, key="t")
    sync = st.toggle("Usuarios según la semana: x = x(t)", key="sync")
    if sync:
        x0 = m.x_t(t0)
        st.caption(f"x(t) = {es(x0)} mil usuarios")
    else:
        x0 = st.slider("Usuarios conectados x (miles)", 4.1, 20.0, step=0.1, key="x")
    st.markdown("**Infraestructura**")
    n0 = st.slider("Servidores n", 1, m.MAX_SERVIDORES, key="n")
    st.markdown("---")
    st.caption("Modelo teórico del escenario 3A. Los resultados deben validarse con pruebas de carga.")

# --------------------------------------------------------- cálculo simbólico
xs, ts, ns, ks = sp.symbols("x t n k", positive=True)
T_sym = (5 * xs + 40) / (xs - 4)
Ts_crudo = (xs**2 - 16) / (xs**2 - 4 * xs)
Ts_sym = sp.cancel(Ts_crudo)
X_sym = 20 / (1 + 9 * sp.exp(-sp.Rational(2, 5) * ts))
C_sym = 120 * ns + (4800 + 200 * ks) / ns
dT, dTs, dX = sp.diff(T_sym, xs), sp.diff(Ts_sym, xs), sp.diff(X_sym, ts)
dC = sp.diff(C_sym, ns)
f_dT = sp.lambdify(xs, dT, "numpy")
f_dTs = sp.lambdify(xs, dTs, "numpy")
f_dX = sp.lambdify(ts, dX, "numpy")

orig_def = x0 > 4
xt = m.x_t(t0)
ritmo_t = m.x_der(t0)
dTdt = m.Ts_der(xt) * ritmo_t
mejor = m.mejor_n(k)

# ------------------------------------------------------------------ cabecera
st.markdown(f"""
<div class="banda">
  <span class="chip">SITUACIÓN 3A</span><span class="chip">CÁLCULO DIFERENCIAL 2026-II</span><span class="chip">k = {k}</span>
  <h1>Monitor 3A · ¿Cómo responde la aplicación cuando llegan más usuarios?</h1>
  <p>Comparamos la versión original y la nueva con derivadas, seguimos el crecimiento de usuarios
  y buscamos cuántos servidores cuestan menos. Mueva los controles de la izquierda.</p>
</div>
""", unsafe_allow_html=True)

tarjetas = []
if orig_def:
    cumple_o = m.T(x0) <= umbral
    tarjetas.append(tarjeta(f"Versión original · x = {es(x0, 1)} mil", f"{es(m.T(x0))} s",
            f"T'(x) = {es(m.T_der(x0))} s por mil usuarios", ORIG,
            "Cumple la promesa" if cumple_o else f"No cumple {es(umbral, 1)} s",
            "ok" if cumple_o else "mal"))
else:
    tarjetas.append(tarjeta(f"Versión original · x = {es(x0, 1)} mil", "No definida",
            "x ≤ 4: el modelo da tiempos negativos o infinitos", ORIG, "Fuera del dominio", "mal"))
cumple_n = m.Ts(x0) <= umbral
tarjetas.append(tarjeta(f"Versión nueva · x = {es(x0, 1)} mil", f"{es(m.Ts(x0), 3)} s",
        f"T*'(x) = {es(m.Ts_der(x0), 3)} s por mil usuarios", NUEVA,
        "Cumple la promesa" if cumple_n else f"No cumple {es(umbral, 1)} s",
        "ok" if cumple_n else "mal"))
tarjetas.append(tarjeta(f"Usuarios · semana {es(t0, 1)}", f"{es(xt)} mil",
        f"x'(t) = {es(ritmo_t)} mil por semana", USU,
        "Antes del pico" if t0 < m.T_INFLEXION else "Después del pico", "neutro"))
tarjetas.append(tarjeta(f"Servidores óptimos · k = {k}", f"n = {mejor}",
        f"C = {es(m.costo(mejor, k), 1)} mil $ al mes", COSTO,
        "Coincide con n elegido" if n0 == mejor else f"Elegido: n = {n0}",
        "ok" if n0 == mejor else "neutro"))
st.markdown('<div class="rejilla">' + "".join(tarjetas) + "</div>", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["⏱️ Diagnóstico de versiones", "👥 Crecimiento de usuarios",
     "🖥️ Servidores y costo", "✅ Veredicto", "✏️ Cálculo paso a paso"])

# ------------------------------------------------------------ 1. versiones
with tab1:
    x = np.linspace(4.06, 20, 500)
    xn = np.linspace(0.5, 20, 500)
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08,
                        subplot_titles=("Tiempo de respuesta (s)", "Ritmo de cambio: la derivada"))
    fig.add_hrect(y0=0, y1=umbral, fillcolor=NUEVA, opacity=0.07, line_width=0, row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=m.T(x), name="T(x) original", line=dict(color=ORIG, width=3)), 1, 1)
    fig.add_trace(go.Scatter(x=xn, y=m.Ts(xn), name="T*(x) nueva", line=dict(color=NUEVA, width=3)), 1, 1)
    fig.add_hline(y=umbral, line_dash="dash", line_color="#8A8170", row=1, col=1,
                  annotation_text=f"promesa {es(umbral, 1)} s", annotation_position="top right")
    fig.add_vline(x=4, line_dash="dot", line_color=ORIG, row=1, col=1)
    fig.add_trace(go.Scatter(x=[4], y=[2], mode="markers", name="hueco: T*(4) = 2",
                             marker=dict(size=11, color="#FFFDF9", line=dict(color=NUEVA, width=2.5))), 1, 1)
    # rectas tangentes en x0: la derivada como pendiente
    h = np.linspace(x0 - 1.2, x0 + 1.2, 20)
    if orig_def:
        fig.add_trace(go.Scatter(x=h, y=m.T(x0) + m.T_der(x0) * (h - x0), name="tangente (original)",
                                 line=dict(color=ORIG, dash="dash", width=1.5)), 1, 1)
        fig.add_trace(go.Scatter(x=[x0], y=[m.T(x0)], mode="markers", showlegend=False,
                                 marker=dict(size=10, color=ORIG)), 1, 1)
    fig.add_trace(go.Scatter(x=h, y=m.Ts(x0) + m.Ts_der(x0) * (h - x0), name="tangente (nueva)",
                             line=dict(color=NUEVA, dash="dash", width=1.5)), 1, 1)
    fig.add_trace(go.Scatter(x=[x0], y=[m.Ts(x0)], mode="markers", showlegend=False,
                             marker=dict(size=10, color=NUEVA)), 1, 1)
    fig.add_trace(go.Scatter(x=x, y=f_dT(x), name="T'(x)", line=dict(color=ORIG, width=3)), 1, 2)
    fig.add_trace(go.Scatter(x=xn, y=f_dTs(xn), name="T*'(x)", line=dict(color=NUEVA, width=3)), 1, 2)
    fig.update_yaxes(range=[0, 45], row=1, col=1)
    fig.update_yaxes(range=[-20, 1], row=1, col=2)
    fig.update_xaxes(title_text="usuarios x (miles)", range=[0, 20.5])
    st.plotly_chart(estilo(fig, 460), width="stretch")
    if orig_def:
        st.markdown(
            f"**Lectura:** con **{es(x0, 1)} mil** usuarios, por cada mil usuarios adicionales el modelo "
            f"cambia el tiempo de la original en **{es(m.T_der(x0))} s** y el de la nueva solo en "
            f"**{es(m.Ts_der(x0), 3)} s**. La línea punteada es la tangente: su pendiente es la derivada.")
    st.markdown(
        "<p class='nota'>La original tiene asíntota vertical en x = 4 y nunca baja de 5 s. "
        "La nueva tiene un hueco en x = 4 que se corrige con T*(4) = 2 s, y allí T*'(4) = −0,25 s por mil usuarios.</p>",
        unsafe_allow_html=True)

# ------------------------------------------------------------ 2. usuarios
with tab2:
    t = np.linspace(0, 15, 400)
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08,
                        subplot_titles=("Usuarios x(t) (miles)", "Velocidad de crecimiento x'(t)"))
    fig.add_trace(go.Scatter(x=t, y=20 / (1 + 9 * np.exp(-0.4 * t)), name="x(t)",
                             line=dict(color=USU, width=3), fill="tozeroy",
                             fillcolor="rgba(61,90,128,0.08)"), 1, 1)
    fig.add_hline(y=m.CAPACIDAD, line_dash="dash", line_color="#8A8170", row=1, col=1,
                  annotation_text="capacidad 20 mil", annotation_position="bottom left")
    ht = np.linspace(max(0, t0 - 2), min(15, t0 + 2), 20)
    fig.add_trace(go.Scatter(x=ht, y=xt + ritmo_t * (ht - t0), name="tangente en t",
                             line=dict(color=USU, dash="dash", width=1.5)), 1, 1)
    fig.add_trace(go.Scatter(x=[t0], y=[xt], mode="markers", name=f"semana {es(t0, 1)}",
                             marker=dict(size=10, color=USU)), 1, 1)
    fig.add_trace(go.Scatter(x=[m.T_INFLEXION], y=[10], mode="markers+text", name="punto de inflexión",
                             text=["inflexión"], textposition="middle right",
                             marker=dict(size=13, symbol="diamond", color=COSTO)), 1, 1)
    fig.add_trace(go.Scatter(x=t, y=f_dX(t), name="x'(t)", line=dict(color=COSTO, width=3),
                             fill="tozeroy", fillcolor="rgba(224,164,88,0.15)"), 1, 2)
    fig.add_vline(x=m.T_INFLEXION, line_dash="dot", line_color="#8A8170", row=1, col=2)
    fig.add_trace(go.Scatter(x=[t0], y=[ritmo_t], mode="markers", showlegend=False,
                             marker=dict(size=10, color=USU)), 1, 2)
    fig.update_xaxes(title_text="semana t")
    st.plotly_chart(estilo(fig, 440), width="stretch")
    a, b = st.columns(2)
    a.markdown(
        f"**Pico de crecimiento:** x''(t) = 0 en t = ln 9 / 0,4 ≈ **{es(m.T_INFLEXION)} semanas**, "
        f"con 10 mil usuarios y {es(m.x_der(m.T_INFLEXION), 1)} mil usuarios nuevos por semana. "
        "Después el crecimiento se frena y x(t) tiende a 20 mil.")
    b.markdown(
        f"**Regla de la cadena en la semana {es(t0, 1)}:** dT*/dt = T*'(x(t)) · x'(t) = "
        f"({es(m.Ts_der(xt), 4)}) · ({es(ritmo_t)}) ≈ **{es(dTdt, 3)} s por semana**.")

# ------------------------------------------------------------ 3. costos
with tab3:
    n = np.arange(1, m.MAX_SERVIDORES + 1)
    nc = np.linspace(1, m.MAX_SERVIDORES, 300)
    pen = (4800 + 200 * k) / n
    fig = go.Figure()
    fig.add_trace(go.Bar(x=n, y=120 * n, name="servidores (120 c/u)", marker_color="#9DB4C0"))
    fig.add_trace(go.Bar(x=n, y=pen, name="penalidades", marker_color=COSTO))
    fig.add_trace(go.Scatter(x=nc, y=[m.costo(v, k) for v in nc], name="C(n) continua",
                             line=dict(color=TINTA, width=2.5)))
    fig.add_trace(go.Scatter(x=[mejor], y=[m.costo(mejor, k)], mode="markers+text",
                             name=f"mínimo entero n = {mejor}", text=[f"n = {mejor}"],
                             textposition="top center", marker=dict(size=16, symbol="star", color=NUEVA)))
    fig.add_vline(x=m.n_optimo_continuo(k), line_dash="dot", line_color=NUEVA,
                  annotation_text=f"n* ≈ {es(m.n_optimo_continuo(k))}")
    fig.update_layout(barmode="stack", title=f"Costo mensual con k = {k} (miles de pesos)")
    fig.update_xaxes(title_text="servidores n", dtick=1)
    st.plotly_chart(estilo(fig, 430), width="stretch")
    ns_c = m.n_optimo_continuo(k)
    vecinos = [v for v in (int(np.floor(ns_c)), int(np.ceil(ns_c))) if 1 <= v <= 20]
    st.markdown(
        f"C'(n) = 120 − (4800 + 200k)/n² = 0 ⟹ **n\\* = √(40 + 5k/3) ≈ {es(ns_c)}**. "
        "Como n debe ser entero, se comparan los vecinos: " +
        " · ".join(f"C({v}) = {es(m.costo(v, k), 1)}" for v in vecinos) +
        f". Gana **n = {mejor}**. Con los n = {n0} elegidos, el costo es {es(m.costo(n0, k), 1)} mil pesos.")
    kc = np.linspace(1, 100, 400)
    kk = np.arange(1, 101)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=kc, y=[m.n_optimo_continuo(v) for v in kc], name="n* = √(40 + 5k/3)",
                              line=dict(color=NUEVA, dash="dash", width=2.5)))
    fig2.add_trace(go.Scatter(x=kk, y=[m.mejor_n(int(v)) for v in kk], name="entero de menor costo",
                              line=dict(color=TINTA, width=2.5, shape="hvh")))
    fig2.add_trace(go.Scatter(x=[k], y=[mejor], mode="markers+text", name=f"k elegido = {k}",
                              text=[f"k = {k} → n = {mejor}"],
                              textposition="top right" if k < 70 else "top left",
                              marker=dict(size=13, color=COSTO, line=dict(color=TINTA, width=1))))
    fig2.update_layout(title="Servidores óptimos según k")
    fig2.update_xaxes(title_text="parámetro k")
    fig2.update_yaxes(title_text="servidores", dtick=1)
    st.plotly_chart(estilo(fig2, 380), width="stretch")
    st.markdown(
        "**¿Qué pasa si sube k?** n* crece como una raíz cuadrada: si k se duplica, los servidores no se duplican. "
        "Con k = 5 conviene 7, con k = 10 conviene 8 y con k = 20 conviene 9.")

# ------------------------------------------------------------ 4. veredicto
with tab4:
    st.markdown(f"#### Recomendación para la empresa (según el modelo, con k = {k})")
    st.markdown(f"""
<div class="veredicto" style="--c:{NUEVA}"><h4>1 · Publicar la versión nueva</h4>
Responde entre 1 y 2 s con más de 4 mil usuarios y casi no cambia con la carga.
La original nunca baja de 5 s, así que no puede cumplir una promesa de {es(umbral, 1)} s.</div>
<div class="veredicto" style="--c:{COSTO}"><h4>2 · Contratar {mejor} servidores</h4>
Es el entero de menor costo: {es(m.costo(mejor, k), 1)} mil pesos al mes (n* ≈ {es(m.n_optimo_continuo(k))}).</div>
<div class="veredicto" style="--c:{USU}"><h4>3 · Reforzar antes de la semana {es(m.T_INFLEXION, 1)}</h4>
Ahí los usuarios crecen más rápido (2 mil por semana) y se llega a 10 mil; después el crecimiento se frena hacia 20 mil.</div>
<div class="veredicto" style="--c:#8A8170"><h4>Condición</h4>
Son resultados teóricos: deben comprobarse con pruebas de carga reales antes de anunciar la promesa.</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------ 5. paso a paso
with tab5:
    st.markdown("##### Versión original: regla del cociente")
    st.latex(r"T(x)=\frac{5x+40}{x-4}\;\Rightarrow\;T'(x)=\frac{5(x-4)-(5x+40)(1)}{(x-4)^2}=" + sp.latex(sp.simplify(dT)))
    st.markdown("##### Versión nueva: simplificar, límite y derivada")
    st.latex(r"T^{*}(x)=\frac{x^2-16}{x^2-4x}=\frac{(x-4)(x+4)}{x(x-4)}=" + sp.latex(Ts_sym) +
             r"\qquad \lim_{x\to4}T^{*}(x)=" + sp.latex(sp.limit(Ts_crudo, xs, 4)) +
             r"\qquad T^{*\prime}(x)=" + sp.latex(sp.simplify(dTs)))
    st.markdown("##### Usuarios: derivada y regla de la cadena")
    st.latex(r"x'(t)=\frac{72e^{-0.4t}}{(1+9e^{-0.4t})^2}\qquad \frac{dT^{*}}{dt}=T^{*\prime}(x(t))\cdot x'(t)")
    st.markdown("##### Servidores: óptimo con la derivada")
    st.latex(r"C'(n)=120-\frac{4800+200k}{n^2}=0\;\Rightarrow\;n^{*}=\sqrt{40+\tfrac{5k}{3}}\qquad C''(n)=\frac{2(4800+200k)}{n^3}>0")
    st.markdown("##### Verificación: derivada simbólica (SymPy) frente a numérica")
    hh = 1e-5
    filas = []
    if orig_def:
        filas.append(("T'(x)", es(x0, 1), es(float(f_dT(x0)), 5), es((m.T(x0 + hh) - m.T(x0 - hh)) / (2 * hh), 5)))
    filas.append(("T*'(x)", es(x0, 1), es(float(f_dTs(x0)), 5), es((m.Ts(x0 + hh) - m.Ts(x0 - hh)) / (2 * hh), 5)))
    filas.append(("x'(t)", es(t0, 1), es(float(f_dX(t0)), 5), es((m.x_t(t0 + hh) - m.x_t(t0 - hh)) / (2 * hh), 5)))
    st.table({"Derivada": [f[0] for f in filas], "Punto": [f[1] for f in filas],
              "Simbólica": [f[2] for f in filas], "Numérica (h = 0,00001)": [f[3] for f in filas]})

st.markdown("<div class='pie'>Monitor 3A · Equipo B (Análisis) y Equipo A (Organización) · "
            "Cálculo diferencial 2026-II · Modelo teórico</div>", unsafe_allow_html=True)
