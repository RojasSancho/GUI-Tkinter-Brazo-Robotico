import tkinter as tk 
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")  # modo oscuro
ctk.set_default_color_theme("dark-blue")  # tema azul

# Click al boton de modo manual del brazo robotico
def activar_manual():
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo manual?")
    if respuesta:  
        print("El usuario eligió Sí")
    else:  
        print("El usuario eligió No")

# Click al boton de modo rutinario del brazo robotico
def activar_rutina():
    respuesta = messagebox.askyesno("Confirmación", "¿Activar modo de rutina?")
    if respuesta:
        print("El usuario eligió Sí")
    else:
        print("El usuario eligió No")

# Funcion para simular conexion o desconexion presionando led
def toggle_led(event=None):
    if label_led.cget("text") == "Desconectado":
        canvas_led_conexion.itemconfig(led_conexion, fill="green")  # cambiar a verde
        label_led.configure(text="Conectado")  # actualizar texto
    else:  # si el LED está en verde (conectado)
        canvas_led_conexion.itemconfig(led_conexion, fill="red")  # cambiar a rojo
        label_led.configure(text="Desconectado")  # actualizar texto

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

# ---------------- Primer grid ----------------
ventana.grid_columnconfigure(0, weight=1) # Mantener centrados los elementos de la columna 0 si la ventana se agranda
ventana.grid_rowconfigure(0, weight=0)  # fila del mensaje de bienvenida
ventana.grid_rowconfigure(1, weight=0)  # fila del boton para manual
ventana.grid_rowconfigure(2, weight=0)  # fila del boton para rutina
ventana.grid_rowconfigure(3, weight=0)  # fila vacia para "empujar" el boton salir
ventana.grid_rowconfigure(4, weight=1)  # fila del switch para modo claro u oscuro
ventana.grid_rowconfigure(5, weight=0)  # fila del boton para salir
ventana.grid_rowconfigure(6, weight=0)  # fila del boton para salir

# Etiqueta de bienvenida a la aplicacion
etiqueta = ctk.CTkLabel(ventana, text="¡Bienvenido!\nControl de brazo robótico\nEstilo pinza".lower(), font=("Bebas Neue", 30))
etiqueta.grid(row=0, column=0, pady=30)

# Boton para entrar en modo rutinario
boton_rutina = ctk.CTkButton(ventana, text="Modo de Rutina 🔄", 
                            font=("Bebas Neue", 50), 
                            width=365, #en pixeles
                            height=60, #en pixeles
                            corner_radius=13,
                            command=activar_rutina)
boton_rutina.grid(row=1, column=0, pady=10)

# Boton para entrar en modo manual
boton_manual = ctk.CTkButton(ventana, text="Modo Manual 🎮", 
                            font=("Bebas Neue", 50), 
                            width=365, #en pixeles
                            height=60, #en pixeles
                            corner_radius=13,
                            command=activar_manual)
boton_manual.grid(row=2, column=0, pady=10)

# LED indicador de conexion con el robot
# Frame contenedor del led y su texto
frame_led = ctk.CTkFrame(ventana, fg_color="transparent")
frame_led.grid(row=3, column=0, pady=10)

# Canvas que contiene el led
canvas_led_conexion = tk.Canvas(frame_led, 
                                width=40, 
                                height=40,
                                highlightthickness=0, 
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

# Switch para modo claro o modo oscuro del app
switch_apariencia = ctk.CTkSwitch(ventana, text = "MODO CLARO / MODO OSCURO", command=cambiar_apariencia)
switch_apariencia.grid(row=5, column=0, pady=15)

# Boton para salir de la aplicacion
boton_salir = ctk.CTkButton(ventana, text="Salir", 
                            font=("Bebas Neue", 30), 
                            width=70, 
                            height=30,
                            corner_radius=13, 
                            command=activar_salir)
boton_salir.grid(row=6, column=0, pady=15)

# Loop para mantener ventana activa
ventana.mainloop()
