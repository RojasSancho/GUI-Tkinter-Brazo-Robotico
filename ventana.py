import tkinter as tk 
from tkinter import messagebox

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
ventana = tk.Tk()
ventana.title("Brazo Robótico")
ventana.geometry("1800x1000")  
ventana.configure(bg="#19183B")

# ---------------- Primer grid ----------------
# Configurar el frame para que centre la columna y la fila
ventana.grid_columnconfigure(0, weight=1)

# Configurar filas y el ancho de las mismas
ventana.grid_rowconfigure(0, weight=0)  # fila del mensaje de bienvenida
ventana.grid_rowconfigure(1, weight=0)  # fila del boton para manual
ventana.grid_rowconfigure(2, weight=0)  # fila del boton para rutina

# Etiqueta de bienvenida a la aplicacion
etiqueta = tk.Label(ventana, text="¡Bienvenido!\nControl de brazo robótico\nEstilo pinza", font=("Bebas Neue", 30), fg="white")
etiqueta.config(bg="#19183B")
etiqueta.grid(row=0, column=0, pady=30)

# Boton para entrar en modo manual
boton_manual = tk.Button(ventana, text="           Modo Manual 🕹️", command=activar_manual, font=("Bebas Neue", 50), width=25, height=1)
boton_manual.grid(row=1, column=0, pady=10)

# Boton para entrar en modo rutinario
boton_rutina = tk.Button(ventana, text="   Modo de Rutina 🔄", command=activar_rutina, font=("Bebas Neue", 50), width=25, height=1)
boton_rutina.grid(row=2, column=0, pady=10)

# ---------------- Segundo grid independiente ----------------
frame_nuevo = tk.Frame(ventana, bg="#19183B")  # color de fondo opcional
frame_nuevo.grid(row=3, column=0, sticky="nsew", padx=20, pady=20)

# Configurar filas y columnas del nuevo grid
for i in range(2):  # 2 filas
    frame_nuevo.grid_rowconfigure(i, weight=1)
for j in range(2):  # 2 columnas
    frame_nuevo.grid_columnconfigure(j, weight=1)

# Agregar botones u otros elementos al nuevo grid
tk.Button(frame_nuevo, text="Botón A").grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
tk.Button(frame_nuevo, text="Botón B").grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
tk.Button(frame_nuevo, text="Botón C").grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
tk.Button(frame_nuevo, text="Salir").grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

# Hacer que la fila del frame se expanda
ventana.grid_rowconfigure(3, weight=1)

# Loop para mantener ventana activa
ventana.mainloop()
