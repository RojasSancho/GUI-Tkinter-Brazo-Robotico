import tkinter as tk 
import customtkinter as ctk
from tkinter import messagebox

from arduinodectector import ArduinoDetector 
from modoautomatico import ModoAutomata

# ------------------------------
# Variables de estado
# ------------------------------
modo_actual = None  # "MANUAL" o "RUTINA"
arduino_conectado = False  # Indicador de conexión (simulado aquí)

ctk.set_appearance_mode("light")  # modo oscuro
ctk.set_default_color_theme("dark-blue")  # tema azul

# Click al boton de modo manual del brazo robotico
def activar_manual():
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo manual?")
    if respuesta:  
        print("El usuario eligió Sí")
        modo_actual = "MANUAL"
        
    else:  
        print("El usuario eligió No")

# Click al boton de modo rutinario del brazo robotico
def activar_rutina():
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo de rutina?")
    if respuesta:
        print("El usuario eligió Sí")
        modo_actual = "RUTINA"
        ventana.destroy()
        app = ModoAutomata()
    else:
        print("El usuario eligió No")

# Funcion para simular conexion o desconexion presionando led

detector = ArduinoDetector()#Instancia a la clase arduinodectector


def toggle_led(event=None):
    if detector.detectar():  # ✅ Llama correctamente al método con 'self'
        canvas_led_conexion.itemconfig(led_conexion, fill="green")
        label_led.configure(text=f"Conectado en {detector.obtener_puerto()}")
    else:
        canvas_led_conexion.itemconfig(led_conexion, fill="red")
        label_led.configure(text="Desconectado")

# Funcion para cambiar de modo oscuro a claro, o viceversa
def cambiar_apariencia():
    if switch_apariencia.get():
        ctk.set_appearance_mode("dark")  # modo oscuro
        canvas_led_conexion.config(bg=ventana.cget("bg"))
    else:
        ctk.set_appearance_mode("light")  # modo oscuro
        canvas_led_conexion.config(bg=ventana.cget("bg"))

# Click al boton de salir
def activar_salir():
    """Cierra la ventana principal."""
    respuesta = messagebox.askyesno("Confirmación", "¿Deseas salir de la aplicación?")
    if respuesta:
        print("El usuario eligió Sí")
        ventana.destroy()
    else:
        print("El usuario eligió No")

# Creacion de ventana principal, configurar tamano, titulo y color de fondo
ventana = ctk.CTk()
ventana.title("Brazo Robótico")
ventana.geometry("800x600")  
ventana.minsize(800, 600)  # tamaño mínimo

tabview = ctk.CTkTabview(ventana, width=780, height=500)
tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Crear las pestañas
tabview.add("Principal")  # pestaña principal
tabview.add("Configuración")  # pestaña de configuración

# ---------------- Primer grid ----------------
ventana.grid_columnconfigure(0, weight=1) # Mantener centrados los elementos de la columna 0 si la ventana se agranda
ventana.grid_rowconfigure(0, weight=1)  # fila del mensaje de bienvenida
ventana.grid_rowconfigure(1, weight=0)  # fila del boton para manual


frame_principal = tabview.tab("Principal")
frame_principal.grid_columnconfigure(0, weight=1)  # centro horizontal
frame_principal.grid_rowconfigure(0, weight=0)  # opcional para centrar verticalmente
frame_principal.grid_rowconfigure(1, weight=0)
frame_principal.grid_rowconfigure(2, weight=0)
frame_principal.grid_rowconfigure(3, weight=1) # espacio flexible debajo
# Etiqueta de bienvenida a la aplicacion
etiqueta = ctk.CTkLabel(frame_principal, text="¡Bienvenido!\nControl de brazo robótico\nEstilo pinza", font=("Bebas Neue", 30))
etiqueta.grid(row=0, column=0, pady=60)

# Boton para entrar en modo rutinario
boton_rutina = ctk.CTkButton(frame_principal, text="Modo de Rutina 🔄", 
                            font=("Bebas Neue", 50), 
                            width=365, #en pixeles
                            height=60, #en pixeles
                            corner_radius=13,
                            command=activar_rutina)
boton_rutina.grid(row=1, column=0, pady=10)

# Boton para entrar en modo manual
boton_manual = ctk.CTkButton(frame_principal, text="Modo Manual 🎮", 
                            font=("Bebas Neue", 50), 
                            width=365, #en pixeles
                            height=60, #en pixeles
                            corner_radius=13,
                            command=activar_manual)
boton_manual.grid(row=2, column=0, pady=10)

frame_inferior = ctk.CTkFrame(ventana, fg_color="transparent")
frame_inferior.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
# Configurar columnas
frame_inferior.grid_columnconfigure(0, weight=1)  # columna izquierda
frame_inferior.grid_columnconfigure(1, weight=1)  # columna derecha

# LED indicador de conexion con el robot
# Frame contenedor del led y su texto
frame_led = ctk.CTkFrame(frame_inferior, fg_color="transparent")
frame_led.grid(row=0, column=0, pady=10, sticky="w")
frame_led.grid_columnconfigure(0, weight=0)  # Canvas
frame_led.grid_columnconfigure(1, weight=0)  # Label
frame_led.grid_columnconfigure(2, weight=1)  # espacio flexible

# Canvas que contiene el led
canvas_led_conexion = tk.Canvas(frame_led, 
                                width=40, 
                                height=40,
                                highlightthickness=0, 
                                bd=0,
                                bg=ventana.cget("bg"))
canvas_led_conexion.grid(row=0, column=0, pady=10)
canvas_led_conexion.bind("<Button-1>", toggle_led)

# Dibujar circulo (Led apagado o rojo)
led_conexion = canvas_led_conexion.create_oval(5,5,35,35,fill="red")

# Label para el texto al lado del led
label_led = ctk.CTkLabel(frame_led, 
                        text="Desconectado", 
                        font=("Bebas Neue", 30))
label_led.grid(row=0, column=1, pady=10)

# Boton para salir de la aplicacion
boton_salir = ctk.CTkButton(frame_inferior, text="Salir", 
                            font=("Bebas Neue", 30), 
                            width=70, 
                            height=30,
                            corner_radius=13, 
                            command=activar_salir)
boton_salir.grid(row=0, column=1, pady=10, sticky="e")

# -------------Pestaña de Configuracion-----------------

frame_config = tabview.tab("Configuración")
# Switch para modo claro o modo oscuro del app
switch_apariencia = ctk.CTkSwitch(frame_config, text = "MODO CLARO / MODO OSCURO", command=cambiar_apariencia)
switch_apariencia.grid(row=0, column=0, pady=20, padx=20)
# Loop para mantener ventana activa

ventana.mainloop()
