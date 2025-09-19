import tkinter as tk 
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")  # modo oscuro
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

# Creacion de ventana principal, configurar tamano, titulo y color de fondo
ventana = ctk.CTk()
ventana.title("Brazo Robótico")
ventana.geometry("800x600")  
ventana.configure(bg="#19183B")

# ---------------- Primer grid ----------------
ventana.grid_columnconfigure(0, weight=1)
ventana.grid_rowconfigure(0, weight=0)  # fila del mensaje de bienvenida
ventana.grid_rowconfigure(1, weight=0)  # fila del boton para manual
ventana.grid_rowconfigure(2, weight=0)  # fila del boton para rutina

# Etiqueta de bienvenida a la aplicacion
etiqueta = ctk.CTkLabel(ventana, text="¡Bienvenido!\nControl de brazo robótico\nEstilo pinza", font=("Bebas Neue", 30))
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

# Boton para salir de la aplicacion
boton_salir = ctk.CTkButton(ventana, text="Salir", 
                            font=("Bebas Neue", 50), 
                            width=200, 
                            height=60,
                            corner_radius=13, 
                            command=None)
boton_salir.grid(row=3, column=0, pady=100)

# Loop para mantener ventana activa
ventana.mainloop()
