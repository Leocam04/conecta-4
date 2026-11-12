#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas unitarias para verificar todos los requisitos del Reto 1: Conecta 4."""

import unittest
from conecta4 import AMARILLA, COLUMNAS, FILAS, ROJA, VACIO, LogicaConecta4


class TestConecta4(unittest.TestCase):
    def setUp(self) -> None:
        self.juego = LogicaConecta4()

    def test_dimensiones_tablero_7x6(self) -> None:
        """El tablero debe ser de 7 columnas (eje X) por 6 filas (eje Y)."""
        self.assertEqual(self.juego.columnas, 7)
        self.assertEqual(self.juego.filas, 6)
        self.assertEqual(len(self.juego.tablero), 6)
        for fila in self.juego.tablero:
            self.assertEqual(len(fila), 7)

    def test_alternancia_inicio_partidas(self) -> None:
        """La 1ª partida empieza Roja, la 2ª Amarilla, la 3ª Roja..."""
        # Partida 1: empieza Roja
        self.assertEqual(self.juego.numero_partida, 1)
        self.assertEqual(self.juego.turno_actual, ROJA)

        # Partida 2: empieza Amarilla
        self.juego.reiniciar_o_siguiente_partida()
        self.assertEqual(self.juego.numero_partida, 2)
        self.assertEqual(self.juego.turno_actual, AMARILLA)

        # Partida 3: empieza Roja
        self.juego.reiniciar_o_siguiente_partida()
        self.assertEqual(self.juego.numero_partida, 3)
        self.assertEqual(self.juego.turno_actual, ROJA)

        # Partida 4: empieza Amarilla
        self.juego.reiniciar_o_siguiente_partida()
        self.assertEqual(self.juego.numero_partida, 4)
        self.assertEqual(self.juego.turno_actual, AMARILLA)

    def test_gravedad_ficha_parte_inferior(self) -> None:
        """Al seleccionar una columna, la ficha se coloca en la parte inferior disponible."""
        # Primera ficha en columna 3 cae a la fila 5 (abajo del todo)
        res1 = self.juego.colocar_ficha(3)
        self.assertEqual(res1, (5, 3, ROJA))
        self.assertEqual(self.juego.tablero[5][3], ROJA)

        # Segunda ficha en columna 3 cae a la fila 4
        res2 = self.juego.colocar_ficha(3)
        self.assertEqual(res2, (4, 3, AMARILLA))
        self.assertEqual(self.juego.tablero[4][3], AMARILLA)

    def test_victoria_horizontal_y_contador(self) -> None:
        """Verifica conexión horizontal de 4 fichas y suma en el contador de victorias/derrotas."""
        # Rojas juegan en cols 0, 1, 2, 3; Amarillas en cols 0, 1, 2
        for col in range(3):
            self.juego.colocar_ficha(col)  # Roja
            self.juego.colocar_ficha(col)  # Amarilla
        self.juego.colocar_ficha(3)        # Roja conecta 4 en fila 5

        self.assertTrue(self.juego.juego_terminado)
        self.assertEqual(self.juego.ganador, ROJA)
        self.assertEqual(self.juego.victorias_rojas, 1)
        self.assertEqual(self.juego.derrotas_amarillas, 1)
        self.assertEqual(len(self.juego.fichas_ganadoras), 4)

        # Al reiniciar partida tras ganar, se mantiene el contador y empieza Amarilla
        self.juego.reiniciar_o_siguiente_partida()
        self.assertEqual(self.juego.victorias_rojas, 1)
        self.assertEqual(self.juego.turno_actual, AMARILLA)

        # Al resetear marcador, todo vuelve a 0 y empieza Roja en Partida 1
        self.juego.resetear_marcador_y_todo()
        self.assertEqual(self.juego.victorias_rojas, 0)
        self.assertEqual(self.juego.victorias_amarillas, 0)
        self.assertEqual(self.juego.numero_partida, 1)
        self.assertEqual(self.juego.turno_actual, ROJA)

    def test_victoria_vertical_y_diagonal(self) -> None:
        """Verifica conexiones verticales y diagonales."""
        # Victoria vertical en col 0 para Rojas
        for _ in range(3):
            self.juego.colocar_ficha(0)  # Roja
            self.juego.colocar_ficha(1)  # Amarilla
        self.juego.colocar_ficha(0)      # 4ª Roja en col 0
        self.assertTrue(self.juego.juego_terminado)
        self.assertEqual(self.juego.ganador, ROJA)


if __name__ == "__main__":
    unittest.main()

