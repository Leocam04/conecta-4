#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONECTA 4 - Edición Clásica Retro (Estilo Windows 95 / Windows XP)
Aplicación de escritorio para PC creada en Python (Tkinter estándar).

Requisitos implementados:
- Tablero de 7x6 (7 columnas en el eje X y 6 filas en el eje Y).
- Fichas Rojas y Amarillas. La 1ª partida la comienza siempre la Roja,
  la 2ª la Amarilla, la 3ª la Roja, alternándose sucesivamente.
- Modo 2 jugadores reales alternándose en el mismo PC.
- Al seleccionar una columna, la ficha cae hasta la parte inferior disponible.
- Marcador persistente en sesión de victorias y derrotas de cada equipo.
- Dos botones principales:
    1) Reiniciar la partida en marcha (o iniciar la siguiente al terminar).
    2) Resetear el contador de victorias y derrotas.
- Estética clásica de juegos de Windows 95 / 98 / XP (biseles 3D, barra de menú,
  contadores digitales estilo LED de 7 segmentos, barra de estado inferior).
"""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List, Optional, Tuple


# ============================================================================
# CONSTANTES DEL JUEGO Y PALETA RETRO WINDOWS 95 / XP
# ============================================================================
COLUMNAS = 7  # Eje X
FILAS = 6     # Eje Y

VACIO = 0
ROJA = 1
AMARILLA = 2

# Colores clásicos del sistema Windows 95 / 98 / XP Clásico
WIN_GRIS = "#d4d0c8"          # Gris clásico de ventana Win95/2000/XP
WIN_GRIS_CLARO = "#ffffff"    # Bisel iluminado superior/izquierdo
WIN_GRIS_OSCURO = "#808080"   # Bisel sombreado inferior/derecho
WIN_NEGRO = "#000000"         # Sombra profunda y fondo de displays LED
WIN_AZUL_TITULO = "#000080"   # Azul clásico de barra activa Windows 95
WIN_AZUL_XP = "#0a246a"       # Azul degradado clásico Windows XP
WIN_TEXTO_BLANCO = "#ffffff"

# Colores del tablero clásico plástico azul
TABLERO_AZUL = "#003399"
TABLERO_BISEL_LUZ = "#3366cc"
TABLERO_BISEL_SOMBRA = "#001a4d"
HUECO_FONDO = "#b8b4ac"
HUECO_HOVER = "#dcd8d0"

# Colores de Ficha Roja (con biselado 3D retro)
ROJA_BASE = "#cc0000"
ROJA_LUZ = "#ff5555"
ROJA_SOMBRA = "#660000"
ROJA_GUIA = "#e69999"

# Colores de Ficha Amarilla (con biselado 3D retro)
AMARILLA_BASE = "#ffcc00"
AMARILLA_LUZ = "#ffff80"
AMARILLA_SOMBRA = "#806600"
AMARILLA_GUIA = "#efe099"

# Display digital LED (estilo Buscaminas / Solitario clásico)
LED_FONDO = "#000000"
LED_ROJO = "#ff1a1a"
LED_VERDE = "#00e600"
LED_AMARILLO = "#ffff00"


# ============================================================================
# LÓGICA DEL JUEGO (DESACOPLADA DE LA INTERFAZ)
# ============================================================================
class LogicaConecta4:
    """Gestiona el estado del tablero 7x6, turnos, victorias/derrotas y reglas."""

    def __init__(self) -> None:
        self.columnas: int = COLUMNAS
        self.filas: int = FILAS

        # Estadísticas acumuladas mientras la aplicación está abierta
        self.victorias_rojas: int = 0
        self.victorias_amarillas: int = 0
        self.empates: int = 0

        # Control de número de partida para alternar quién empieza:
        # Partida 1 -> Roja, Partida 2 -> Amarilla, Partida 3 -> Roja...
        self.numero_partida: int = 1
        self.jugador_inicial: int = ROJA
        self.turno_actual: int = ROJA

        # Estado del tablero: matriz [fila][columna], donde fila 0 es arriba y fila 5 es abajo
        self.tablero: List[List[int]] = []
        self.historial_movimientos: List[Tuple[int, int, int]] = []
        self.juego_terminado: bool = False
        self.ganador: Optional[int] = None
        self.fichas_ganadoras: List[Tuple[int, int]] = []

        self._inicializar_tablero()

    def _inicializar_tablero(self) -> None:
        """Limpia la matriz 6x7 y prepara el turno según el jugador inicial de la partida."""
        self.tablero = [[VACIO for _ in range(self.columnas)] for _ in range(self.filas)]
        self.historial_movimientos.clear()
        self.juego_terminado = False
        self.ganador = None
        self.fichas_ganadoras = []
        self.turno_actual = self.jugador_inicial

    def obtener_fila_disponible(self, col: int) -> Optional[int]:
        """Devuelve la fila más baja libre (mayor índice Y) en la columna indicada, o None si está llena."""
        if col < 0 or col >= self.columnas:
            return None
        for fila in range(self.filas - 1, -1, -1):
            if self.tablero[fila][col] == VACIO:
                return fila
        return None

    def colocar_ficha(self, col: int) -> Optional[Tuple[int, int, int]]:
        """
        Intenta colocar una ficha del jugador actual en la columna seleccionada.
        Devuelve (fila, col, jugador) si tuvo éxito, o None si el movimiento no es válido.
        """
        if self.juego_terminado:
            return None

        fila = self.obtener_fila_disponible(col)
        if fila is None:
            return None

        jugador = self.turno_actual
        self.tablero[fila][col] = jugador
        self.historial_movimientos.append((fila, col, jugador))

        # Comprobar si esta jugada genera un Conecta 4
        coordenadas_ganadoras = self.buscar_conecta_4(fila, col, jugador)
        if coordenadas_ganadoras:
            self.juego_terminado = True
            self.ganador = jugador
            self.fichas_ganadoras = coordenadas_ganadoras
            if jugador == ROJA:
                self.victorias_rojas += 1
            else:
                self.victorias_amarillas += 1
        elif len(self.historial_movimientos) == self.filas * self.columnas:
            # Tablero lleno sin ganador -> Empate
            self.juego_terminado = True
            self.ganador = VACIO
            self.empates += 1
        else:
            # Alternar turno entre los dos jugadores dentro de la misma partida
            self.turno_actual = AMARILLA if self.turno_actual == ROJA else ROJA

        return (fila, col, jugador)

    def buscar_conecta_4(self, fila_origen: int, col_origen: int, jugador: int) -> List[Tuple[int, int]]:
        """
        Verifica si el jugador ha conectado 4 o más fichas en horizontal, vertical o diagonal
        a partir de la última ficha colocada en (fila_origen, col_origen).
        """
        direcciones = [
            (0, 1),   # Horizontal (—)
            (1, 0),   # Vertical (|)
            (1, 1),   # Diagonal principal (\)
            (1, -1),  # Diagonal secundaria (/)
        ]

        for df, dc in direcciones:
            linea = [(fila_origen, col_origen)]

            # Explorar en sentido positivo
            f, c = fila_origen + df, col_origen + dc
            while 0 <= f < self.filas and 0 <= c < self.columnas and self.tablero[f][c] == jugador:
                linea.append((f, c))
                f += df
                c += dc

            # Explorar en sentido negativo
            f, c = fila_origen - df, col_origen - dc
            while 0 <= f < self.filas and 0 <= c < self.columnas and self.tablero[f][c] == jugador:
                linea.insert(0, (f, c))
                f -= df
                c -= dc

            if len(linea) >= 4:
                return linea

        return []

    def reiniciar_o_siguiente_partida(self) -> None:
        """
        Inicia la siguiente partida alternando el jugador inicial:
        1ª partida: Roja, 2ª partida: Amarilla, 3ª partida: Roja...
        """
        self.numero_partida += 1
        self.jugador_inicial = ROJA if (self.numero_partida % 2 == 1) else AMARILLA
        self._inicializar_tablero()

    def resetear_marcador_y_todo(self) -> None:
        """
        Resetea el contador de victorias, derrotas y empates a 0,
        y reinicia el ciclo a la 1ª partida (comenzando siempre la Roja).
        """
        self.victorias_rojas = 0
        self.victorias_amarillas = 0
        self.empates = 0
        self.numero_partida = 1
        self.jugador_inicial = ROJA
        self._inicializar_tablero()

    @property
    def derrotas_rojas(self) -> int:
        return self.victorias_amarillas

    @property
    def derrotas_amarillas(self) -> int:
        return self.victorias_rojas


# ============================================================================
# INTERFAZ GRÁFICA RETRO ESTILO WINDOWS 95 / WINDOWS XP
# ============================================================================
class AplicacionConecta4Retro:
    """Interfaz clásica estilo Windows 95 / XP (Buscaminas / Solitario)."""

    TAMANO_CELDA = 64
    MARGEN_TABLERO = 14
    RADIO_FICHA = 24

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Conecta 4 - Windows Classic Edition")
        self.root.configure(bg=WIN_GRIS)
        self.root.resizable(False, False)

        self.logica = LogicaConecta4()

        # Nombres de ambos equipos
        self.nombre_rojas = "Jugador 1 (Rojas)"
        self.nombre_amarillas = "Jugador 2 (Amarillas)"

        # Estado visual
        self.columna_hover: Optional[int] = None
        self.animacion_en_curso: bool = False
        self.parpadeo_ganador: bool = True
        self.tiempo_inicio_partida: float = time.time()
        self.botones_columna: List[tk.Button] = []

        self.ancho_canvas = COLUMNAS * self.TAMANO_CELDA + 2 * self.MARGEN_TABLERO
        self.alto_canvas = FILAS * self.TAMANO_CELDA + 2 * self.MARGEN_TABLERO

        self._construir_menu_clasico()
        self._construir_interfaz_retro()
        self._vincular_eventos()
        self._actualizar_interfaz_completa()
        self._iniciar_bucle_reloj()
        self._centrar_ventana()

    # ------------------------------------------------------------------------
    # BARRA DE MENÚ CLÁSICA DE WINDOWS 95 / XP
    # ------------------------------------------------------------------------
    def _construir_menu_clasico(self) -> None:
        barra_menu = tk.Menu(self.root, bg=WIN_GRIS, fg=WIN_NEGRO, relief=tk.FLAT)

        menu_juego = tk.Menu(barra_menu, tearoff=0, bg=WIN_GRIS, fg=WIN_NEGRO)
        menu_juego.add_command(
            label="Reiniciar partida / Siguiente (F2)",
            command=self.accion_reiniciar_partida,
        )
        menu_juego.add_command(
            label="Resetear contador de victorias y derrotas",
            command=self.accion_resetear_marcador,
        )
        menu_juego.add_separator()
        menu_juego.add_command(
            label="Cambiar nombres de jugadores...",
            command=self.accion_personalizar_nombres,
        )
        menu_juego.add_separator()
        menu_juego.add_command(label="Salir", command=self.root.quit)
        barra_menu.add_cascade(label="Juego", menu=menu_juego)

        menu_ayuda = tk.Menu(barra_menu, tearoff=0, bg=WIN_GRIS, fg=WIN_NEGRO)
        menu_ayuda.add_command(label="Reglas del Reto 1...", command=self._mostrar_acerca_de)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.root.config(menu=barra_menu)

    # ------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ RETRO 3D
    # ------------------------------------------------------------------------
    def _construir_interfaz_retro(self) -> None:
        # Marco exterior elevado con bisel clásico de Windows 95
        marco_exterior = tk.Frame(
            self.root,
            bg=WIN_GRIS,
            bd=3,
            relief=tk.RAISED,
            padx=10,
            pady=10,
        )
        marco_exterior.pack(fill=tk.BOTH, expand=True)

        # 1. BARRA DE TÍTULO INTERNA ESTILO WINDOWS 95 / XP
        barra_banner = tk.Frame(
            marco_exterior,
            bg=WIN_AZUL_TITULO,
            bd=2,
            relief=tk.RAISED,
            padx=8,
            pady=4,
        )
        barra_banner.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            barra_banner,
            text="❖ CONECTA 4 — EDICIÓN CLÁSICA DE ESCRITORIO (7x6)",
            font=("MS Sans Serif", 10, "bold"),
            fg=WIN_TEXTO_BLANCO,
            bg=WIN_AZUL_TITULO,
        ).pack(side=tk.LEFT)

        self.lbl_partida_cabecera = tk.Label(
            barra_banner,
            text="Partida N° 01 | Inicia: ROJA",
            font=("MS Sans Serif", 9, "bold"),
            fg="#ffff80",
            bg=WIN_AZUL_TITULO,
        )
        self.lbl_partida_cabecera.pack(side=tk.RIGHT)

        # 2. PANEL SUPERIOR HUNDIDO ESTILO "BUSCAMINAS" (LEDs + Carita + Estado)
        panel_superior = tk.Frame(
            marco_exterior,
            bg=WIN_GRIS,
            bd=3,
            relief=tk.SUNKEN,
            padx=10,
            pady=6,
        )
        panel_superior.pack(fill=tk.X, pady=(0, 10))

        # Display LED izquierdo: Contador de Partida / Jugadas
        frame_led_izq = tk.Frame(panel_superior, bg=WIN_GRIS)
        frame_led_izq.pack(side=tk.LEFT)
        tk.Label(
            frame_led_izq,
            text="FICHAS",
            font=("MS Sans Serif", 7, "bold"),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
        ).pack()
        self.lbl_led_fichas = tk.Label(
            frame_led_izq,
            text="00/42",
            font=("Courier New", 15, "bold"),
            bg=LED_FONDO,
            fg=LED_ROJO,
            bd=2,
            relief=tk.SUNKEN,
            padx=6,
            pady=1,
        )
        self.lbl_led_fichas.pack()

        # Centro: Indicador de turno clásico con botón de carita estilo Buscaminas
        frame_centro_estado = tk.Frame(panel_superior, bg=WIN_GRIS)
        frame_centro_estado.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=12)

        self.btn_carita = tk.Button(
            frame_centro_estado,
            text=":-)",
            font=("Courier New", 11, "bold"),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            activebackground=WIN_GRIS,
            bd=3,
            relief=tk.RAISED,
            width=5,
            cursor="hand2",
            command=self.accion_reiniciar_partida,
        )
        self.btn_carita.pack(pady=(0, 3))

        self.lbl_banner_turno = tk.Label(
            frame_centro_estado,
            text="TURNO ACTUAL: FICHAS ROJAS",
            font=("MS Sans Serif", 10, "bold"),
            bg=LED_FONDO,
            fg=LED_AMARILLO,
            bd=2,
            relief=tk.SUNKEN,
            padx=10,
            pady=3,
        )
        self.lbl_banner_turno.pack(fill=tk.X)

        # Display LED derecho: Reloj en segundos estilo Windows 95
        frame_led_der = tk.Frame(panel_superior, bg=WIN_GRIS)
        frame_led_der.pack(side=tk.RIGHT)
        tk.Label(
            frame_led_der,
            text="TIEMPO",
            font=("MS Sans Serif", 7, "bold"),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
        ).pack()
        self.lbl_led_tiempo = tk.Label(
            frame_led_der,
            text="000",
            font=("Courier New", 15, "bold"),
            bg=LED_FONDO,
            fg=LED_ROJO,
            bd=2,
            relief=tk.SUNKEN,
            padx=8,
            pady=1,
        )
        self.lbl_led_tiempo.pack()

        # 3. CUERPO PRINCIPAL: MARCADOR ROJO + TABLERO 7x6 + MARCADOR AMARILLO
        frame_cuerpo = tk.Frame(marco_exterior, bg=WIN_GRIS)
        frame_cuerpo.pack(fill=tk.BOTH, expand=True)

        # Panel lateral izquierdo: Equipo Rojo
        self.panel_rojo = self._crear_panel_equipo_retro(
            parent=frame_cuerpo,
            titulo_marco=" Equipo Rojo ",
            color_ficha=ROJA_BASE,
            color_luz=ROJA_LUZ,
            color_sombra=ROJA_SOMBRA,
            es_rojo=True,
        )
        self.panel_rojo.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Zona central: Botones de columna 1..7 + Tablero 7x6 hundido
        frame_zona_tablero = tk.Frame(
            frame_cuerpo,
            bg=WIN_GRIS,
            bd=3,
            relief=tk.RAISED,
            padx=8,
            pady=8,
        )
        frame_zona_tablero.pack(side=tk.LEFT)

        # Fila de 7 botones clásicos 3D para soltar ficha en cada columna
        frame_botones_col = tk.Frame(
            frame_zona_tablero,
            bg=WIN_GRIS,
            padx=self.MARGEN_TABLERO,
        )
        frame_botones_col.pack(fill=tk.X, pady=(0, 6))

        for col in range(COLUMNAS):
            btn_col = tk.Button(
                frame_botones_col,
                text=f"▼ {col + 1}",
                font=("MS Sans Serif", 9, "bold"),
                bg=WIN_GRIS,
                fg=WIN_NEGRO,
                activebackground="#e4e0d8",
                bd=3,
                relief=tk.RAISED,
                width=6,
                cursor="hand2",
                command=lambda c=col: self.intentar_jugada_columna(c),
            )
            btn_col.grid(row=0, column=col, padx=2, sticky="ew")
            frame_botones_col.grid_columnconfigure(col, weight=1)
            self.botones_columna.append(btn_col)

        # Marco hundido para el tablero 7x6
        marco_canvas = tk.Frame(
            frame_zona_tablero,
            bg=WIN_GRIS_OSCURO,
            bd=4,
            relief=tk.SUNKEN,
        )
        marco_canvas.pack()

        self.canvas = tk.Canvas(
            marco_canvas,
            width=self.ancho_canvas,
            height=self.alto_canvas,
            bg=TABLERO_AZUL,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack()

        # Panel lateral derecho: Equipo Amarillo
        self.panel_amarillo = self._crear_panel_equipo_retro(
            parent=frame_cuerpo,
            titulo_marco=" Equipo Amarillo ",
            color_ficha=AMARILLA_BASE,
            color_luz=AMARILLA_LUZ,
            color_sombra=AMARILLA_SOMBRA,
            es_rojo=False,
        )
        self.panel_amarillo.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))

        # 4. BARRA DE BOTONES DE CONTROL (SOLO LOS DOS BOTONES REQUERIDOS + NOMBRES)
        frame_botones_accion = tk.Frame(
            marco_exterior,
            bg=WIN_GRIS,
            bd=2,
            relief=tk.GROOVE,
            padx=10,
            pady=8,
        )
        frame_botones_accion.pack(fill=tk.X, pady=(10, 0))

        # Botón Requisito 1: Reiniciar la partida en marcha
        self.btn_reiniciar = tk.Button(
            frame_botones_accion,
            text="Reiniciar Partida en Marcha (F2)",
            font=("MS Sans Serif", 9, "bold"),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            activebackground="#e4e0d8",
            bd=3,
            relief=tk.RAISED,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.accion_reiniciar_partida,
        )
        self.btn_reiniciar.pack(side=tk.LEFT, padx=(0, 10))

        # Botón Requisito 2: Resetear el contador de victorias y derrotas
        self.btn_resetear = tk.Button(
            frame_botones_accion,
            text="Resetear Contador de Victorias y Derrotas",
            font=("MS Sans Serif", 9, "bold"),
            bg=WIN_GRIS,
            fg="#800000",
            activebackground="#e4e0d8",
            bd=3,
            relief=tk.RAISED,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.accion_resetear_marcador,
        )
        self.btn_resetear.pack(side=tk.LEFT)

        # Botón auxiliar clásico para editar nombres de los 2 jugadores
        self.btn_nombres = tk.Button(
            frame_botones_accion,
            text="Nombres...",
            font=("MS Sans Serif", 9),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            activebackground="#e4e0d8",
            bd=3,
            relief=tk.RAISED,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.accion_personalizar_nombres,
        )
        self.btn_nombres.pack(side=tk.RIGHT)

        # 5. BARRA DE ESTADO INFERIOR CLÁSICA DE WINDOWS 95
        frame_statusbar = tk.Frame(self.root, bg=WIN_GRIS, padx=4, pady=2)
        frame_statusbar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status_izq = tk.Label(
            frame_statusbar,
            text=" Listo. Haz clic en una columna o usa las teclas 1 a 7.",
            font=("MS Sans Serif", 8),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            bd=1,
            relief=tk.SUNKEN,
            anchor="w",
            padx=4,
        )
        self.lbl_status_izq.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.lbl_status_centro = tk.Label(
            frame_statusbar,
            text=" 1ª Partida: Inicia Roja ",
            font=("MS Sans Serif", 8),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            bd=1,
            relief=tk.SUNKEN,
            width=24,
        )
        self.lbl_status_centro.pack(side=tk.LEFT, padx=(0, 3))

        tk.Label(
            frame_statusbar,
            text=" Tablero: 7x6 ",
            font=("MS Sans Serif", 8),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            bd=1,
            relief=tk.SUNKEN,
            width=14,
        ).pack(side=tk.RIGHT)

    def _crear_panel_equipo_retro(
        self,
        parent: tk.Widget,
        titulo_marco: str,
        color_ficha: str,
        color_luz: str,
        color_sombra: str,
        es_rojo: bool,
    ) -> tk.LabelFrame:
        """Crea un cuadro de grupo estilo Windows 95 (GroupBox) con contadores LED."""
        grupo = tk.LabelFrame(
            parent,
            text=titulo_marco,
            font=("MS Sans Serif", 9, "bold"),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            bd=2,
            relief=tk.GROOVE,
            width=175,
            padx=10,
            pady=8,
        )
        grupo.pack_propagate(False)

        # Icono de la ficha con relieve 3D retro
        canvas_ficha = tk.Canvas(
            grupo,
            width=56,
            height=56,
            bg=WIN_GRIS,
            bd=2,
            relief=tk.SUNKEN,
            highlightthickness=0,
        )
        canvas_ficha.pack(pady=(4, 6))
        canvas_ficha.create_oval(9, 9, 51, 51, fill=color_sombra, outline=WIN_NEGRO)
        canvas_ficha.create_oval(7, 7, 49, 49, fill=color_ficha, outline=color_luz, width=2)
        canvas_ficha.create_oval(14, 14, 42, 42, fill=color_ficha, outline=color_sombra, width=2)

        # Nombre del jugador en recuadro hundido
        lbl_nombre = tk.Label(
            grupo,
            text=self.nombre_rojas if es_rojo else self.nombre_amarillas,
            font=("MS Sans Serif", 9, "bold"),
            bg="#ffffff",
            fg=WIN_NEGRO,
            bd=2,
            relief=tk.SUNKEN,
            padx=4,
            pady=3,
            wraplength=145,
        )
        lbl_nombre.pack(fill=tk.X, pady=(0, 8))

        # Indicador luminoso de turno
        lbl_estado_equipo = tk.Label(
            grupo,
            text="SU TURNO",
            font=("MS Sans Serif", 8, "bold"),
            bg=LED_FONDO,
            fg=LED_VERDE,
            bd=2,
            relief=tk.SUNKEN,
            pady=3,
        )
        lbl_estado_equipo.pack(fill=tk.X, pady=(0, 10))

        # Contador digital de VICTORIAS
        tk.Label(
            grupo,
            text="Partidas Ganadas (Victorias):",
            font=("MS Sans Serif", 8),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            anchor="w",
        ).pack(fill=tk.X)

        lbl_victorias = tk.Label(
            grupo,
            text="000",
            font=("Courier New", 18, "bold"),
            bg=LED_FONDO,
            fg=LED_VERDE,
            bd=2,
            relief=tk.SUNKEN,
            pady=2,
        )
        lbl_victorias.pack(fill=tk.X, pady=(2, 8))

        # Contador digital de DERROTAS
        tk.Label(
            grupo,
            text="Partidas Perdidas (Derrotas):",
            font=("MS Sans Serif", 8),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            anchor="w",
        ).pack(fill=tk.X)

        lbl_derrotas = tk.Label(
            grupo,
            text="000",
            font=("Courier New", 16, "bold"),
            bg=LED_FONDO,
            fg=LED_ROJO,
            bd=2,
            relief=tk.SUNKEN,
            pady=2,
        )
        lbl_derrotas.pack(fill=tk.X, pady=(2, 8))

        # Contador de Empates
        lbl_empates = tk.Label(
            grupo,
            text="Empates: 0",
            font=("MS Sans Serif", 8),
            bg=WIN_GRIS,
            fg=WIN_NEGRO,
            bd=1,
            relief=tk.SUNKEN,
            pady=3,
        )
        lbl_empates.pack(fill=tk.X, pady=(4, 0))

        if es_rojo:
            self.lbl_nombre_rojo = lbl_nombre
            self.lbl_turno_rojo = lbl_estado_equipo
            self.lbl_victorias_rojas = lbl_victorias
            self.lbl_derrotas_rojas = lbl_derrotas
            self.lbl_empates_rojas = lbl_empates
        else:
            self.lbl_nombre_amarillo = lbl_nombre
            self.lbl_turno_amarillo = lbl_estado_equipo
            self.lbl_victorias_amarillas = lbl_victorias
            self.lbl_derrotas_amarillas = lbl_derrotas
            self.lbl_empates_amarillas = lbl_empates

        return grupo

    # ------------------------------------------------------------------------
    # EVENTOS DE RATÓN Y TECLADO
    # ------------------------------------------------------------------------
    def _vincular_eventos(self) -> None:
        self.canvas.bind("<Motion>", self._al_mover_raton)
        self.canvas.bind("<Leave>", self._al_salir_raton)
        self.canvas.bind("<Button-1>", self._al_hacer_clic_tablero)

        # Teclas 1 a 7 para seleccionar columna y F2 para reiniciar partida (estándar Win95)
        for num_col in range(1, COLUMNAS + 1):
            self.root.bind(
                str(num_col),
                lambda evento, c=num_col - 1: self.intentar_jugada_columna(c),
            )
            self.root.bind(
                f"<KP_{num_col}>",
                lambda evento, c=num_col - 1: self.intentar_jugada_columna(c),
            )

        self.root.bind("<F2>", lambda e: self.accion_reiniciar_partida())
        self.root.bind("<r>", lambda e: self.accion_reiniciar_partida())
        self.root.bind("<R>", lambda e: self.accion_reiniciar_partida())

    def _obtener_columna_desde_x(self, x: int) -> Optional[int]:
        x_rel = x - self.MARGEN_TABLERO
        if x_rel < 0 or x_rel >= COLUMNAS * self.TAMANO_CELDA:
            return None
        col = int(x_rel // self.TAMANO_CELDA)
        return col if 0 <= col < COLUMNAS else None

    def _al_mover_raton(self, event: tk.Event) -> None:
        col = self._obtener_columna_desde_x(event.x)
        if col != self.columna_hover:
            self.columna_hover = col
            if not self.animacion_en_curso:
                self._dibujar_tablero()

    def _al_salir_raton(self, event: tk.Event) -> None:
        if self.columna_hover is not None:
            self.columna_hover = None
            if not self.animacion_en_curso:
                self._dibujar_tablero()

    def _al_hacer_clic_tablero(self, event: tk.Event) -> None:
        if self.logica.juego_terminado and not self.animacion_en_curso:
            self.accion_reiniciar_partida()
            return

        col = self._obtener_columna_desde_x(event.x)
        if col is not None:
            self.intentar_jugada_columna(col)

    # ------------------------------------------------------------------------
    # JUGADA Y CAÍDA DE FICHA A LA PARTE INFERIOR
    # ------------------------------------------------------------------------
    def intentar_jugada_columna(self, col: int) -> None:
        """Coloca la ficha en la fila más baja disponible de la columna seleccionada."""
        if self.animacion_en_curso or self.logica.juego_terminado:
            return

        fila_destino = self.logica.obtener_fila_disponible(col)
        if fila_destino is None:
            self.lbl_status_izq.configure(
                text=f" ¡La columna {col + 1} está llena! Elige otra columna."
            )
            return

        jugador_actual = self.logica.turno_actual
        self.animacion_en_curso = True
        self.btn_carita.configure(text=":-O")

        fila_anim = 0.0

        def paso_caida() -> None:
            nonlocal fila_anim
            if fila_anim < fila_destino:
                fila_anim = min(float(fila_destino), fila_anim + 0.65)
                self._dibujar_tablero(ficha_cayendo=(fila_anim, col, jugador_actual))
                self.root.after(18, paso_caida)
            else:
                self.animacion_en_curso = False
                self.logica.colocar_ficha(col)
                self._actualizar_interfaz_completa()

        paso_caida()

    # ------------------------------------------------------------------------
    # ACCIONES DE LOS DOS BOTONES PRINCIPALES
    # ------------------------------------------------------------------------
    def accion_reiniciar_partida(self) -> None:
        """
        Botón 1: Reinicia la partida en marcha (o inicia la siguiente tras finalizar),
        alternando el equipo que comienza (1ª Roja, 2ª Amarilla, 3ª Roja...).
        """
        if self.animacion_en_curso:
            return

        self.logica.reiniciar_o_siguiente_partida()
        self.tiempo_inicio_partida = time.time()
        self._actualizar_interfaz_completa()

    def accion_resetear_marcador(self) -> None:
        """
        Botón 2: Resetea el contador de victorias y derrotas de ambos equipos a 0
        y devuelve el juego a la Partida #1 (comenzando siempre la Roja).
        """
        if self.animacion_en_curso:
            return

        hay_datos = (
            self.logica.victorias_rojas > 0
            or self.logica.victorias_amarillas > 0
            or self.logica.empates > 0
            or len(self.logica.historial_movimientos) > 0
            or self.logica.numero_partida > 1
        )
        if hay_datos:
            confirmar = messagebox.askyesno(
                "Conecta 4 - Confirmar",
                "¿Desea resetear el contador de victorias y derrotas a 0\n"
                "y volver a la Partida N° 1 (empezando la ficha Roja)?",
                parent=self.root,
            )
            if not confirmar:
                return

        self.logica.resetear_marcador_y_todo()
        self.tiempo_inicio_partida = time.time()
        self._actualizar_interfaz_completa()

    def accion_personalizar_nombres(self) -> None:
        nuevo_rojo = simpledialog.askstring(
            "Jugador 1 (Fichas Rojas)",
            "Nombre del equipo con fichas ROJAS:",
            initialvalue=self.nombre_rojas,
            parent=self.root,
        )
        if nuevo_rojo and nuevo_rojo.strip():
            self.nombre_rojas = nuevo_rojo.strip()[:22]

        nuevo_amarillo = simpledialog.askstring(
            "Jugador 2 (Fichas Amarillas)",
            "Nombre del equipo con fichas AMARILLAS:",
            initialvalue=self.nombre_amarillas,
            parent=self.root,
        )
        if nuevo_amarillo and nuevo_amarillo.strip():
            self.nombre_amarillas = nuevo_amarillo.strip()[:22]

        self._actualizar_interfaz_completa()

    def _mostrar_acerca_de(self) -> None:
        messagebox.showinfo(
            "Acerca de Conecta 4 - Reto 1",
            "Conecta 4 — Edición Clásica para PC (Windows 95 / XP Style)\n\n"
            "• Tablero de 7x6 (7 columnas x 6 filas).\n"
            "• 1ª partida inicia Roja, 2ª Amarilla, 3ª Roja...\n"
            "• Dos jugadores alternándose en el mismo PC.\n"
            "• Marcador de victorias y derrotas en sesión.",
            parent=self.root,
        )

    # ------------------------------------------------------------------------
    # DIBUJO DEL TABLERO RETRO 7x6 EN EL CANVAS
    # ------------------------------------------------------------------------
    def _centro_celda(self, fila: float, col: int) -> Tuple[float, float]:
        x = self.MARGEN_TABLERO + col * self.TAMANO_CELDA + self.TAMANO_CELDA / 2
        y = self.MARGEN_TABLERO + fila * self.TAMANO_CELDA + self.TAMANO_CELDA / 2
        return (x, y)

    def _dibujar_ficha_retro(
        self, x: float, y: float, jugador: int, radio: float = RADIO_FICHA, guia: bool = False
    ) -> None:
        """Dibuja una ficha Roja o Amarilla con biselado clásico 3D de los años 90."""
        if jugador == ROJA:
            base = ROJA_GUIA if guia else ROJA_BASE
            luz = ROJA_LUZ
            sombra = ROJA_SOMBRA
        else:
            base = AMARILLA_GUIA if guia else AMARILLA_BASE
            luz = AMARILLA_LUZ
            sombra = AMARILLA_SOMBRA

        if guia:
            self.canvas.create_oval(
                x - radio + 3,
                y - radio + 3,
                x + radio - 3,
                y + radio - 3,
                fill=base,
                outline=WIN_NEGRO,
                width=1,
                dash=(3, 3),
            )
            return

        # Sombra inferior derecha (efecto 3D)
        self.canvas.create_oval(
            x - radio + 1,
            y - radio + 1,
            x + radio + 1,
            y + radio + 1,
            fill=sombra,
            outline=WIN_NEGRO,
            width=1,
        )
        # Cuerpo principal de la ficha
        self.canvas.create_oval(
            x - radio,
            y - radio,
            x + radio,
            y + radio,
            fill=base,
            outline=luz,
            width=2,
        )
        # Anillo concéntrico tallado clásico
        r_interno = radio * 0.68
        self.canvas.create_oval(
            x - r_interno,
            y - r_interno,
            x + r_interno,
            y + r_interno,
            fill=base,
            outline=sombra,
            width=2,
        )

    def _dibujar_tablero(
        self, ficha_cayendo: Optional[Tuple[float, int, int]] = None
    ) -> None:
        self.canvas.delete("all")

        # Cuadrícula biselada estilo Windows 95 sobre el tablero azul
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                x1 = self.MARGEN_TABLERO + col * self.TAMANO_CELDA
                y1 = self.MARGEN_TABLERO + fila * self.TAMANO_CELDA
                x2 = x1 + self.TAMANO_CELDA
                y2 = y1 + self.TAMANO_CELDA

                # Bisel claro arriba/izquierda y oscuro abajo/derecha de cada celda
                self.canvas.create_line(x1, y2, x1, y1, x2, y1, fill=TABLERO_BISEL_LUZ, width=2)
                self.canvas.create_line(x1, y2, x2, y2, x2, y1, fill=TABLERO_BISEL_SOMBRA, width=2)

        # Determinar casilla destino inferior si el cursor está sobre una columna
        fila_guia: Optional[int] = None
        if (
            self.columna_hover is not None
            and not self.logica.juego_terminado
            and not self.animacion_en_curso
        ):
            fila_guia = self.logica.obtener_fila_disponible(self.columna_hover)

        conjunto_ganadoras = set(self.logica.fichas_ganadoras)

        # Dibujar los 42 huecos circulares y las fichas colocadas
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                cx, cy = self._centro_celda(fila, col)
                estado = self.logica.tablero[fila][col]

                # Sombra interior del hueco circular
                self.canvas.create_oval(
                    cx - self.RADIO_FICHA - 2,
                    cy - self.RADIO_FICHA - 2,
                    cx + self.RADIO_FICHA + 2,
                    cy + self.RADIO_FICHA + 2,
                    fill=TABLERO_BISEL_SOMBRA,
                    outline=TABLERO_BISEL_LUZ,
                    width=1,
                )

                if estado == VACIO:
                    es_hover = col == self.columna_hover and fila == fila_guia
                    self.canvas.create_oval(
                        cx - self.RADIO_FICHA,
                        cy - self.RADIO_FICHA,
                        cx + self.RADIO_FICHA,
                        cy + self.RADIO_FICHA,
                        fill=HUECO_HOVER if es_hover else HUECO_FONDO,
                        outline=WIN_NEGRO,
                        width=1,
                    )
                    if es_hover:
                        self._dibujar_ficha_retro(
                            cx, cy, self.logica.turno_actual, guia=True
                        )
                else:
                    self._dibujar_ficha_retro(cx, cy, estado)

                    # Resaltado parpadeante clásico sobre las 4 fichas ganadoras
                    if (fila, col) in conjunto_ganadoras and self.parpadeo_ganador:
                        self.canvas.create_oval(
                            cx - self.RADIO_FICHA - 3,
                            cy - self.RADIO_FICHA - 3,
                            cx + self.RADIO_FICHA + 3,
                            cy + self.RADIO_FICHA + 3,
                            outline="#ffffff",
                            width=3,
                        )

        # Si hay una ficha en plena caída, dibujarla
        if ficha_cayendo is not None:
            fila_c, col_c, jug_c = ficha_cayendo
            cx, cy = self._centro_celda(fila_c, col_c)
            self._dibujar_ficha_retro(cx, cy, jug_c)

        # Trazar línea recta sobre las 4 fichas conectadas al ganar
        if len(self.logica.fichas_ganadoras) >= 4:
            f1, c1 = self.logica.fichas_ganadoras[0]
            f2, c2 = self.logica.fichas_ganadoras[-1]
            x1, y1 = self._centro_celda(f1, c1)
            x2, y2 = self._centro_celda(f2, c2)
            self.canvas.create_line(x1, y1, x2, y2, fill=WIN_NEGRO, width=6)
            self.canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=3)

    # ------------------------------------------------------------------------
    # ACTUALIZACIÓN DE TODOS LOS CONTROLES E INDICADORES
    # ------------------------------------------------------------------------
    def _actualizar_interfaz_completa(self) -> None:
        # Cabecera y barra de estado: quién inició esta partida
        color_inicio = "ROJA" if self.logica.jugador_inicial == ROJA else "AMARILLA"
        self.lbl_partida_cabecera.configure(
            text=f"Partida N° {self.logica.numero_partida:02d} | Inicia: {color_inicio}"
        )
        self.lbl_status_centro.configure(
            text=f" Partida #{self.logica.numero_partida}: Inicia {color_inicio} "
        )

        # LED de fichas jugadas
        num_movs = len(self.logica.historial_movimientos)
        self.lbl_led_fichas.configure(text=f"{num_movs:02d}/42")

        # Marcadores digitales de Victorias y Derrotas
        self.lbl_nombre_rojo.configure(text=self.nombre_rojas)
        self.lbl_nombre_amarillo.configure(text=self.nombre_amarillas)

        self.lbl_victorias_rojas.configure(text=f"{self.logica.victorias_rojas:03d}")
        self.lbl_derrotas_rojas.configure(text=f"{self.logica.derrotas_rojas:03d}")
        self.lbl_empates_rojas.configure(text=f"Empates: {self.logica.empates}")

        self.lbl_victorias_amarillas.configure(text=f"{self.logica.victorias_amarillas:03d}")
        self.lbl_derrotas_amarillas.configure(text=f"{self.logica.derrotas_amarillas:03d}")
        self.lbl_empates_amarillas.configure(text=f"Empates: {self.logica.empates}")

        # Habilitar/deshabilitar botones superiores de columna según disponibilidad
        for col, btn in enumerate(self.botones_columna):
            col_disponible = (
                not self.logica.juego_terminado
                and self.logica.obtener_fila_disponible(col) is not None
            )
            btn.configure(state=tk.NORMAL if col_disponible else tk.DISABLED)

        # Estado de la partida (en curso vs terminada)
        siguiente_color = "AMARILLA" if self.logica.jugador_inicial == ROJA else "ROJA"

        if self.logica.juego_terminado:
            self.btn_reiniciar.configure(
                text=f"Siguiente Partida (#{self.logica.numero_partida + 1} - Inicia {siguiente_color})"
            )
            if self.logica.ganador == ROJA:
                self.btn_carita.configure(text="B-)")
                self.lbl_banner_turno.configure(
                    text=f"¡GANADOR: {self.nombre_rojas.upper()}!",
                    fg=LED_VERDE,
                )
                self.lbl_turno_rojo.configure(text="¡VICTORIA!", fg=LED_VERDE)
                self.lbl_turno_amarillo.configure(text="DERROTA", fg=LED_ROJO)
                self.lbl_status_izq.configure(
                    text=(
                        f" ¡4 en línea de {self.nombre_rojas}! Pulsa 'Siguiente Partida' "
                        f"(la Partida #{self.logica.numero_partida + 1} la empieza {siguiente_color})."
                    )
                )
            elif self.logica.ganador == AMARILLA:
                self.btn_carita.configure(text="B-)")
                self.lbl_banner_turno.configure(
                    text=f"¡GANADOR: {self.nombre_amarillas.upper()}!",
                    fg=LED_VERDE,
                )
                self.lbl_turno_amarillo.configure(text="¡VICTORIA!", fg=LED_VERDE)
                self.lbl_turno_rojo.configure(text="DERROTA", fg=LED_ROJO)
                self.lbl_status_izq.configure(
                    text=(
                        f" ¡4 en línea de {self.nombre_amarillas}! Pulsa 'Siguiente Partida' "
                        f"(la Partida #{self.logica.numero_partida + 1} la empieza {siguiente_color})."
                    )
                )
            else:
                self.btn_carita.configure(text=":-|")
                self.lbl_banner_turno.configure(
                    text="¡EMPATE! TABLERO LLENO",
                    fg=LED_AMARILLO,
                )
                self.lbl_turno_rojo.configure(text="EMPATE", fg=LED_AMARILLO)
                self.lbl_turno_amarillo.configure(text="EMPATE", fg=LED_AMARILLO)
                self.lbl_status_izq.configure(
                    text=(
                        f" Partida empatada. Pulsa 'Siguiente Partida' "
                        f"(la Partida #{self.logica.numero_partida + 1} la empieza {siguiente_color})."
                    )
                )
        else:
            self.btn_carita.configure(text=":-)")
            self.btn_reiniciar.configure(text="Reiniciar Partida en Marcha (F2)")
            if self.logica.turno_actual == ROJA:
                self.lbl_banner_turno.configure(
                    text=f"► TURNO: {self.nombre_rojas.upper()} [ROJA]",
                    fg="#ff6666",
                )
                self.lbl_turno_rojo.configure(text="► JUGANDO", fg=LED_VERDE)
                self.lbl_turno_amarillo.configure(text="EN ESPERA", fg="#808080")
                self.lbl_status_izq.configure(
                    text=f" Turno de {self.nombre_rojas} (Ficha Roja). Selecciona una columna (1-7)."
                )
            else:
                self.lbl_banner_turno.configure(
                    text=f"► TURNO: {self.nombre_amarillas.upper()} [AMARILLA]",
                    fg=LED_AMARILLO,
                )
                self.lbl_turno_amarillo.configure(text="► JUGANDO", fg=LED_VERDE)
                self.lbl_turno_rojo.configure(text="EN ESPERA", fg="#808080")
                self.lbl_status_izq.configure(
                    text=f" Turno de {self.nombre_amarillas} (Ficha Amarilla). Selecciona una columna (1-7)."
                )

        self._actualizar_led_tiempo()
        self._dibujar_tablero()

    def _actualizar_led_tiempo(self) -> None:
        segundos = min(999, int(time.time() - self.tiempo_inicio_partida))
        self.lbl_led_tiempo.configure(text=f"{segundos:03d}")

    def _iniciar_bucle_reloj(self) -> None:
        if not self.logica.juego_terminado:
            self._actualizar_led_tiempo()
        elif self.logica.fichas_ganadoras and not self.animacion_en_curso:
            self.parpadeo_ganador = not self.parpadeo_ganador
            self._dibujar_tablero()

        self.root.after(450, self._iniciar_bucle_reloj)

    def _centrar_ventana(self) -> None:
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = max(0, (self.root.winfo_screenwidth() // 2) - (ancho // 2))
        y = max(0, (self.root.winfo_screenheight() // 2) - (alto // 2) - 20)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================
def main() -> None:
    root = tk.Tk()
    AplicacionConecta4Retro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
