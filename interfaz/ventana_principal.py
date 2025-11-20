"""
ventana_principal.py
--------------------

Ventana principal del sistema/interfaz de control del brazo robótico.

Funciones principales:
- Mostrar la interfaz inicial del proyecto.
- Permitir al usuario elegir entre modo manual o modo de rutina.
- Administrar ventana principal y sus ventanas hijas (ModoManual / ModoAutomatico).
- Verificar continuamente el estado de conexión con el Arduino mediante un LED indicador.

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

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from hardware.arduino_detector import ArduinoDetector
from interfaz.modo_automatico import ModoAutomatico
from interfaz.modo_manual import ModoManual

# ------------------------------
# Variables de estado
# ------------------------------
modo_actual = None  # "MANUAL" o "RUTINA"a

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


# --------------------------------------------------------------------------------
# Funciones auxiliares
# --------------------------------------------------------------------------------
def abrir_modo_manual(ventana, frame_inferior):
    """
    Abre la ventana de modo manual luego de pedir confirmación al usuario.

    Args:
        ventana (CTk): Ventana principal.
        frame_inferior (CTkFrame): Contenedor inferior donde se ubican controles.

    """
    global modo_actual
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo manual?")
    if respuesta:
        modo_actual = "MANUAL"
        ventana.withdraw()  # Ocultar ventana principal

        def volver_al_principal():
            """Restaura la ventana principal después de cerrar ModoManual."""
            ventana.state("zoomed")  # Maximizar primero
            ventana.update_idletasks()  # Forzar redibujo
            ventana.deiconify()  # Muestra de nuevo

        # Abrir ventana de modo manual
        ModoManual(parent=ventana, volver_callback=volver_al_principal)
    else:
        print("Modo Manual cancelado")


def abrir_modo_rutina(ventana, frame_inferior):
    """
    Abre la ventana de modo de rutina luego de pedir confirmación al usuario.

    Args:
        ventana (CTk): Ventana principal.
        frame_inferior (CTkFrame): Contenedor inferior con controles.

    """
    global modo_actual
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo de rutina?")
    if respuesta:
        modo_actual = "RUTINA"
        ventana.withdraw()  # Oculta la ventana principal

        def volver_al_principal():
            """Restaura la ventana principal tras cerrar ModoAutomatico."""
            ventana.state("zoomed")  # Maximizar primero
            ventana.update_idletasks()  # Forzar redibujo
            ventana.deiconify()  # Muestra de nuevo

        # Abrir ventana modo automático
        ModoAutomatico(
            parent=ventana, detector=detector, volver_callback=volver_al_principal
        )
    else:
        print("Modo Rutina cancelado")


def activar_salir(ventana):
    """
    Pregunta al usuario si desea salir y cierra la aplicación si confirma.

    Args:
        ventana (CTk): Ventana principal.

    """
    respuesta = messagebox.askyesno("Confirmación", "¿Deseas salir de la aplicación?")
    if respuesta:
        ventana.destroy()


# --------------------------------------------------------------------------------
# Función principal de ejecución
# --------------------------------------------------------------------------------
def ejecutar_app():
    """
    Punto de entrada de la aplicación/interfaz:

    Inicializa la ventana principal del sistema, configura el layout general,
    crea los tabs, botones de navegación, detector de Arduino y ciclo de actualización
    del estado de conexión.
    """
    ventana = ctk.CTk()
    ventana.title("Brazo Robótico")
    ventana.after(0, lambda: ventana.state("zoomed"))
    ventana.minsize(800, 600)

    # Inicializar detector de Arduino
    global detector
    detector = ArduinoDetector()
    estado_arduino_anterior = detector.estado_arduino
    ventana.after(2000, lambda: intentar_conexion_inicial(detector))

    # --------------------------------------------------
    # LED / texto para mostrar estado de conexión
    # --------------------------------------------------
    def actualizar_estado_led(event=None):
        """
        Actualiza el LED y el texto con el estado actual del Arduino.
        """
        if detector.detectar():
            canvas_led_conexion.itemconfig(led_conexion, fill="green")
            label_led.configure(text=f"Conectado en {detector.obtener_puerto()}")
        else:
            canvas_led_conexion.itemconfig(led_conexion, fill="red")
            label_led.configure(text="Desconectado")

    def cambiar_apariencia():
        """
        Alterna entre modo claro y oscuro de la interfaz gráfica.
        """
        if switch_apariencia.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        canvas_led_conexion.config(bg=ventana.cget("bg"))

    # --------------------------------------------------
    # Layout principal con tabs (pestañas)
    # --------------------------------------------------
    tabview = ctk.CTkTabview(ventana, width=780, height=500)
    tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tabview.add("Principal")
    tabview.add("Configuración")

    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_rowconfigure(0, weight=1)
    ventana.grid_rowconfigure(1, weight=0)

    # --------------------------------------------------
    # Pestaña: Principal
    # --------------------------------------------------
    frame_principal = tabview.tab("Principal")
    frame_principal.grid_columnconfigure(0, weight=1)
    for i in range(4):
        frame_principal.grid_rowconfigure(i, weight=0 if i < 3 else 1)

    etiqueta = ctk.CTkLabel(
        frame_principal,
        text="¡Bienvenido!\nControl de brazo robótico\nEstilo pinza",
        font=("Bebas Neue", 30),
    )
    etiqueta.grid(row=0, column=0, pady=60)

    # --------------------------------------------------
    # Botones de modo
    # --------------------------------------------------
    frame_inferior = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_inferior.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
    frame_inferior.grid_columnconfigure(0, weight=1)
    frame_inferior.grid_columnconfigure(1, weight=1)

    boton_rutina = ctk.CTkButton(
        frame_principal,
        text="Modo de Rutina 🔄",
        font=("Bebas Neue", 50),
        width=365,
        height=60,
        corner_radius=13,
        command=lambda: abrir_modo_rutina(ventana, frame_inferior),
    )
    boton_rutina.grid(row=1, column=0, pady=10)

    boton_manual = ctk.CTkButton(
        frame_principal,
        text="Modo Manual 🎮",
        font=("Bebas Neue", 50),
        width=365,
        height=60,
        corner_radius=13,
        command=lambda: abrir_modo_manual(ventana, frame_inferior),
    )
    boton_manual.grid(row=2, column=0, pady=10)

    # --------------------------------------------------
    # Indicador LED de conexión y botón Salir
    # --------------------------------------------------
    frame_led = ctk.CTkFrame(frame_inferior, fg_color="transparent")
    frame_led.grid(row=0, column=0, pady=10, sticky="w")
    frame_led.grid_columnconfigure(0, weight=0)
    frame_led.grid_columnconfigure(1, weight=0)
    frame_led.grid_columnconfigure(2, weight=1)

    canvas_led_conexion = tk.Canvas(
        frame_led,
        width=40,
        height=40,
        highlightthickness=0,
        bd=0,
        bg=ventana.cget("bg"),
    )
    canvas_led_conexion.grid(row=0, column=0, pady=10)

    led_conexion = canvas_led_conexion.create_oval(5, 5, 35, 35, fill="red")

    label_led = ctk.CTkLabel(frame_led, text="Desconectado", font=("Bebas Neue", 30))
    label_led.grid(row=0, column=1, pady=10)

    boton_salir = ctk.CTkButton(
        frame_inferior,
        text="Salir",
        font=("Bebas Neue", 30),
        width=70,
        height=30,
        corner_radius=13,
        command=lambda: activar_salir(ventana),
    )
    boton_salir.grid(row=0, column=1, pady=10, sticky="e")

    # ------------------------------
    # Pestaña: Configuración
    # ------------------------------
    frame_config = tabview.tab("Configuración")

    switch_apariencia = ctk.CTkSwitch(
        frame_config, text="MODO CLARO / MODO OSCURO", command=cambiar_apariencia
    )
    switch_apariencia.grid(row=0, column=0, pady=20, padx=20)

    # -------------------------------------------------------------------
    # Rutinas de actualización
    # -------------------------------------------------------------------
    def intentar_conexion_inicial(detector):
        """Realiza un primer intento de detección y conexión al Arduino."""
        if detector.detectar():
            detector.conectar()

    def actualizar_led_gui():
        """
        Refresca continuamente el indicador visual del estado del Arduino
        (LED y texto).
        """
        estado = detector.actualizar_estado()  # devuelve "conectado" o "desconectado"

        if estado == "conectado":
            canvas_led_conexion.itemconfig(led_conexion, fill="green")
            label_led.configure(text=f"Conectado en {detector.obtener_puerto()}")
        else:
            canvas_led_conexion.itemconfig(led_conexion, fill="red")
            label_led.configure(text="Desconectado")

        ventana.after(1000, actualizar_led_gui)

    actualizar_led_gui()

    ventana.mainloop()


# --------------------------------------------------------
# Ejecución directa del módulo
# --------------------------------------------------------
if __name__ == "__main__":
    ejecutar_app()
if __name__ == "__main__":
    ejecutar_app()
