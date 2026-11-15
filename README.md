# Recurso interactivo – Situación 3A: rendimiento de una aplicación web

Cálculo diferencial 2026-II · Actividad final del tercer corte (derivadas en contextos profesionales).

Integrantes: Jhonathan Mayorga y Andrés Morales (Equipo B – Análisis), Hernando Stiven Cortés López (Equipo A – Organización).

## Qué hace

Aplicación en Python (Streamlit, SymPy, Matplotlib) que permite cambiar el parámetro k, los usuarios conectados x,
la semana t, el número de servidores n y el umbral de la promesa comercial, y muestra:

1. El tiempo de respuesta de la versión original T(x) y de la nueva T*(x), con sus derivadas.
2. El crecimiento de usuarios x(t), su ritmo x'(t) y el punto de inflexión (t ≈ 5,49 semanas).
3. El costo mensual C(n) = 120n + (4800 + 200k)/n y el número de servidores de costo mínimo.
4. La recomendación según el modelo.

Todos los resultados son teóricos y deben validarse con pruebas de carga reales.

## Archivos

- `modelo.py`: funciones del modelo (sin interfaz), para revisarlas y probarlas por separado.
- `app.py`: la interfaz interactiva; calcula las derivadas con SymPy y las compara con una derivada numérica.
- `requirements.txt`: librerías necesarias.

## Cómo ejecutarlo en un computador

```
pip install -r requirements.txt
streamlit run app.py
```
