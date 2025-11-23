"""
arduino_detector.py
------------------
Módulo encargado de gestionar la detección y comunicación serial con un
Arduino UNO. Utiliza PySerial para la apertura del puerto, envío de datos,
lectura de respuestas y reconexión automática.

Autores:
    Hermes Rojas Sancho
    Donifer Campos Parra
    Jose Ignacio Goldoni

Curso:
    Lenguaje Ensamblador (CI-0118)
    Proyecto Integrador de Lenguaje Ensamblador y Fundamentos de Arquitectura

Año:
    2025
"""

import serial
import serial.tools.list_ports
import time


# ---------------------------------------------------------------------------
# Para depuración: muestra los dispositivos conectados en puertos serie.
# Esto NO afecta el funcionamiento del programa, solo imprime en consola.
# ---------------------------------------------------------------------------
print("Puertos siendo utilizados:")
puertos = serial.tools.list_ports.comports()
for puerto in puertos:
    print(puerto)


class ArduinoDetector:
    """
    Administra la detección, conexión y comunicación con un Arduino mediante puerto serie. Ofrece funciones para enviar comandos, leer respuestas, limpiar el buffer y verificar el estado físico de la conexión.

    Cuenta con funciones para:
        - detectar el puerto donde está el Arduino,
        - abrir y cerrar la conexión,
        - enviar comandos,
        - leer respuestas,
        - reconectar automáticamente si el Arduino se desconecta,
        - limpiar el buffer serial.

    Atributos:
        puerto (str - None): Nombre del puerto COM donde se encuentra conectado el Arduino.
        conexion (serial.Serial - None): Objeto Serial activo.
        estado_arduino (str): 'conectado' o 'desconectado'.
    """

    def __init__(self):
        """Inicializa el detector sin puerto ni conexión activa."""
        self.puerto = None
        self.conexion = None
        self.estado_arduino = "desconectado"

    # ------------------------------------------------------------------

    def detectar(self):
        """
        Busca un dispositivo reconocido como Arduino en los puertos serie.

        Returns:
            True si encuentra un Arduino o dispositivo compatible,
            False si no hay ninguno conectado.

        """
        puertos = serial.tools.list_ports.comports()

        for puerto in puertos:
            descripcion = puerto.description.lower()

            # Coincidencias típicas encontradas en Windows/Linux/Mac
            if (
                "arduino" in descripcion
                or "usb serial" in descripcion
                or "dispositivo serie" in descripcion
            ):
                # Detecta cambio de puerto
                if self.puerto != puerto.device:
                    self.puerto = puerto.device
                    print("--------------------------")
                    print("Arduino detectado en", self.puerto)

                return True

        # Si estaba conectado y desaparece
        if self.estado_arduino != "desconectado":
            print("---------------------")
            print("Arduino desconectado.")
            self.estado_arduino = "desconectado"
            self.puerto = None

        return False

    # ------------------------------------------------------------------

    def obtener_puerto(self):
        """
        Devuelve el puerto actual asignado al Arduino (si existe).

        Returns:
            str | None: nombre del puerto o None si no está conectado.
        """
        return self.puerto

    # ------------------------------------------------------------------

    def conectar(self, baudrate=9600, timeout=1):
        """
        Intenta abrir la conexión serial con el Arduino.

        Args:
            baudrate (int): Velocidad de comunicación serial.
            timeout (int | float): Tiempo máximo para lecturas bloqueantes.

        Returns:
            bool: True si la conexión fue exitosa, False si no fue posible conectar.
        """
        if not self.puerto:
            return False

        # Cerrar conexión previa si sigue abierta
        if self.conexion and self.conexion.is_open:
            self.conexion.close()

        try:
            self.conexion = serial.Serial(self.puerto, baudrate, timeout=timeout)
            # time.sleep(2)
            self.estado_arduino = "conectado"
            print(f"Conectado al Arduino en {self.puerto}")
            print("Arduino conectado correctamente.")
            return True

        except (serial.SerialException, FileNotFoundError):
            self.estado_arduino = "desconectado"
            return False

    # ------------------------------------------------------------------

    def enviar_rutina(self, rutina, repeticiones):
        """
        Envía un comando de rutina al Arduino y las repeticiones de la misma.

        Args:
            rutina (int): Número de la rutina ejecutada en Arduino.
            repeticiones (int): Cantidad de veces que debe repetirse.

        Returns:
            bool: True si el comando fue enviado correctamente.
                    False si no existe conexión activa.
        """
        if not self.conexion or not self.conexion.is_open:
            print("No existe conexion activa con un Arduino")
            return False

        try:
            mensaje = f"{rutina},{repeticiones}\n"
            self.conexion.write(mensaje.encode("utf-8"))  # Usar UTF-8
            print("--------------------------------")
            print(f"Mensaje enviado al Arduino: {mensaje.strip()}")
            return True

        except serial.SerialException as e:
            print("-----------------------------")
            print(f"Error al enviar datos: {e}")
            return False

    # ------------------------------------------------------------------

    def leer_respuesta(self):
        """
        Lee una línea enviada por el Arduino (si existe).

        Returns:
            str | None: La línea decodificada sin saltos de línea,
                        o None si no hay datos disponibles.
        """
        if not self.conexion or not self.conexion.is_open:
            return None

        try:
            if self.conexion.in_waiting > 0:
                respuesta = (
                    self.conexion.readline().decode("utf-8", errors="ignore").strip()
                )
                return respuesta

        except serial.SerialException:
            return None

        return None

    # ------------------------------------------------------------------

    def cerrar(self):
        """
        Cierra la conexión serial con el Arduino y actualiza el estado.
        """
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            print("Conexion serie con Arduino cerrada.")
        self.estado_arduino = "desconectado"

    # ------------------------------------------------------------------

    def revisar_conexion(self):
        """
        Revisa si el Arduino permanece conectado y maneja la reconexión automática.

        Returns:
            bool: True si el Arduino está conectado o se reconectó.
                    False si no es posible establecer conexión.
        """
        puertos_actuales = [p.device for p in serial.tools.list_ports.comports()]

        # Caso 1: El puerto desapareció físico
        if self.puerto and self.puerto not in puertos_actuales:
            if self.estado_arduino != "desconectado":
                print("---------------------")
                print("Arduino desconectado.")
                self.cerrar()
            self.puerto = None
            self.conexion = None
            self.estado_arduino = "desconectado"
            return False

        # Caso 2: No hay conexión, pero el puerto sí existe → intentar reconectar
        if (not self.conexion or not self.conexion.is_open) and self.detectar():
            if self.estado_arduino != "conectado":
                print("Arduino detectado, intentando reconectar...")
                if self.conectar():
                    self.estado_arduino = "conectado"
                    return True

        # Caso 3: No se detecta el dispositivo
        elif not self.detectar():
            if self.estado_arduino != "desconectado":
                print("---------------------")
                print("Arduino desconectado.")
                self.estado_arduino = "desconectado"

        return self.esta_conectado()

    # ------------------------------------------------------------------

    def esta_conectado(self):
        """
        Indica si la conexión serial está activa.

        Returns:
            bool: True si existe conexión abierta.
        """
        return self.conexion is not None and self.conexion.is_open

    # ------------------------------------------------------------------

    def actualizar_estado(self):
        """
        Actualiza el estado del Arduino revisando su conexión física.

        Returns:
            str: 'conectado' o 'desconectado'.
        """
        if self.revisar_conexion():
            return "conectado"
        else:
            return "desconectado"

    # ------------------------------------------------------------------

    def limpiar_buffer(self):
        """
        Vacía el buffer serial descartando datos residuales.
        Para antes de comenzar comunicación importante.

        Nota:
            Ignora cualquier excepción para evitar interferir con el flujo
            principal del programa.
        """
        try:
            while self.leer_respuesta() is not None:
                pass
        except Exception:
            pass
