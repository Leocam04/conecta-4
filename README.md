# ❖ Conecta 4 — Edición Clásica Retro (Estilo Windows 95 / XP)

Implementación para PC en **Python** del juego clásico **Conecta 4** con interfaz retro inspirada en los juegos de escritorio de **Windows 95 / 98 / XP** (*Buscaminas*, *Solitario*, *Corazones*), cumpliendo todos los requisitos del **Reto 1 de MoureDev**.

---

## ✅ Características y requisitos implementados

- **Estética Retro Windows 95 / XP**:
  - Paneles grises biselados en 3D (`RAISED` y `SUNKEN`), barra de título clásica azul marino y barra de estado inferior con compartimentos.
  - Contadores digitales estilo **LED de 7 segmentos** (fondo negro con dígitos luminosos) y botón central con carita (`:-)`, `:-O`, `B-)`) al estilo *Buscaminas*.
  - Botones superiores de columna (`▼ 1` a `▼ 7`) además de clic directo sobre el tablero.
- **Tablero de 7x6**: 7 columnas en el eje `X` y 6 filas en el eje `Y`.
- **Fichas Rojas y Amarillas con turno inicial alternado**:
  - **1ª partida**: comienza siempre la ficha **Roja**.
  - **2ª partida**: comienza la ficha **Amarilla**.
  - **3ª partida**: comienza la ficha **Roja** (y así sucesivamente).
- **2 jugadores reales alternándose** desde el mismo PC.
- **Caída a la parte inferior**: al seleccionar la columna, la ficha se coloca en la posición libre más baja.
- **Marcador de Victorias y Derrotas**: guarda las partidas ganadas y perdidas de cada equipo mientras la aplicación no se cierra.
- **Dos botones de control principales** (sin sonido ni opción de deshacer):
  1. **Reiniciar Partida en Marcha (`F2`)**: reinicia el tablero y alterna el jugador que inicia la siguiente partida.
  2. **Resetear Contador de Victorias y Derrotas**: pone los marcadores a `000` y vuelve a la **Partida N° 01** (iniciando la Roja).

---

## 🚀 Cómo ejecutar el juego

Haz doble clic en **`iniciar_conecta4.bat`** o ejecuta desde la terminal:

```powershell
python conecta4.py
```
