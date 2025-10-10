import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from hardware.arduino_detector import ArduinoDetector
from interfaz.modo_automatico import ModoAutomatico

# ------------------------------
# Variables de estado
# ------------------------------
modo_actual = None  # "MANUAL" o "RUTINA"
arduino_conectado = False  # Indicador de conexión (simulado aquí)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

# ------------------------------
# Funciones auxiliares
# ------------------------------


def activar_manual():
    global modo_actual
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo manual?")
    if respuesta:
        print("Modo Manual activado")
        modo_actual = "MANUAL"
    else:
        print("Modo Manual cancelado")


def abrir_modo_rutina(ventana, frame_inferior):
    global modo_actual
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo de rutina?")
    if respuesta:
        modo_actual = "RUTINA"
        ventana.withdraw()  # Oculta la ventana principal

        def volver_al_principal():
            ventana.state("zoomed")  # Maximizar primero
            ventana.update_idletasks()  # Forzar redibujo
            ventana.deiconify()

        # Abrir ventana modo automático
        ModoAutomatico(parent=ventana, volver_callback=volver_al_principal)
    else:
        print("Modo Rutina cancelado")


def activar_salir(ventana):
    respuesta = messagebox.askyesno("Confirmación", "¿Deseas salir de la aplicación?")
    if respuesta:
        ventana.destroy()


# ------------------------------
# Ejecutar aplicación
# ------------------------------
def ejecutar_app():
    ventana = ctk.CTk()
    ventana.title("Brazo Robótico")
    ventana.after(0, lambda: ventana.state("zoomed"))
    ventana.minsize(800, 600)

    detector = ArduinoDetector()

    # ------------------------------
    # Función para toggle LED de conexión
    # ------------------------------
    def toggle_led(event=None):
        if detector.detectar():
            canvas_led_conexion.itemconfig(led_conexion, fill="green")
            label_led.configure(text=f"Conectado en {detector.obtener_puerto()}")
        else:
            canvas_led_conexion.itemconfig(led_conexion, fill="red")
            label_led.configure(text="Desconectado")

    def cambiar_apariencia():
        if switch_apariencia.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        canvas_led_conexion.config(bg=ventana.cget("bg"))

    # ------------------------------
    # Layout principal con tabs
    # ------------------------------
    tabview = ctk.CTkTabview(ventana, width=780, height=500)
    tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tabview.add("Principal")
    tabview.add("Configuración")

    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_rowconfigure(0, weight=1)
    ventana.grid_rowconfigure(1, weight=0)

    # ------------------------------
    # Pestaña Principal
    # ------------------------------
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

    # ------------------------------
    # Botones de modo
    # ------------------------------
    frame_inferior = ctk.CTkFrame(
        ventana, fg_color="transparent"
    )  # Frame para pasar a modo automático
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
        command=activar_manual,
    )
    boton_manual.grid(row=2, column=0, pady=10)

    # ------------------------------
    # Parte inferior (LED y salir)
    # ------------------------------
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
    canvas_led_conexion.bind("<Button-1>", toggle_led)

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
    # Pestaña Configuración
    # ------------------------------
    frame_config = tabview.tab("Configuración")
    switch_apariencia = ctk.CTkSwitch(
        frame_config, text="MODO CLARO / MODO OSCURO", command=cambiar_apariencia
    )
    switch_apariencia.grid(row=0, column=0, pady=20, padx=20)

    ventana.mainloop()


if __name__ == "__main__":
    ejecutar_app()
