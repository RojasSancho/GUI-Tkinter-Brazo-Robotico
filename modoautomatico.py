import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class ModoAutomata:
    def __init__(self):
        # ventana principal
        self.ventana_automatico = ctk.CTk()
        self.ventana_automatico.title("Modo automático")
        self.ventana_automatico.geometry("1366x768")
        self.ventana_automatico.minsize(1366, 768)

        # variables
        self.subrutina_elegida = ctk.StringVar(value="")
        self.numero_var = ctk.IntVar(value=0)

        # frames principales
        self.frame_central = ctk.CTkFrame(self.ventana_automatico, width=780, height=500)
        self.frame_central.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_descripcion = ctk.CTkFrame(self.frame_central, width=340, height=200, fg_color="white")
        self.frame_descripcion.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_numero_repeticiones = ctk.CTkFrame(self.frame_central, width=340, height=100)
        self.frame_numero_repeticiones.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_spinner = ctk.CTkFrame(self.frame_central, fg_color="transparent")
        self.frame_spinner.grid(row=4, column=0, padx=20, pady=20)

        self.frame_boton_ejecutar = ctk.CTkFrame(self.frame_central, fg_color="transparent")
        self.frame_boton_ejecutar.grid(row=5, column=0, padx=20, pady=20)

        #  Configuración del grid 
        self.ventana_automatico.grid_columnconfigure(0, weight=1)
        self.ventana_automatico.grid_rowconfigure(0, weight=1)
        self.ventana_automatico.grid_rowconfigure(1, weight=0)

        # Frame inferior
        self.frame_inferior = ctk.CTkFrame(self.ventana_automatico, fg_color="transparent")
        self.frame_inferior.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
        self.frame_inferior.grid_columnconfigure(0, weight=1)
        self.frame_inferior.grid_columnconfigure(1, weight=1)

        # Widgets
        self.crear_widgets()

        #Mainloop ----------
        self.ventana_automatico.mainloop()
    
    #####################
    """ Métodos"""
    #####################
    def activar_salir(self):
        respuesta = messagebox.askyesno("Confirmación", "¿Deseas salir de la aplicación?")
        if respuesta:
            self.ventana_automatico.destroy()

    def optionmenu_callback(self, choice):
        print("Seleccionada rutina:", choice)
        self.subrutina_elegida.set(choice)

    def aumentar(self):
        self.numero_var.set(self.numero_var.get() + 1)

    def disminuir(self):
        valor = self.numero_var.get() - 1
        if valor < 0:
            valor = 0
        self.numero_var.set(valor)

    def ejecutar_rutina(self):
        print(f"Se ejecutará la: {self.subrutina_elegida.get()} {self.numero_var.get()} veces")
       

    def crear_widgets(self):
        # Botón salir
        boton_salir = ctk.CTkButton(self.frame_inferior, text="Salir",
                                    font=("Bebas Neue", 30),
                                    width=70, height=30,
                                    corner_radius=13,
                                    command=self.activar_salir)
        boton_salir.grid(row=0, column=1, pady=10, sticky="e")

        # Label menú
        label_subrutinas = ctk.CTkLabel(self.frame_central,
                                        text="Menú \n de subrutinas pre-programadas",
                                        font=("Bebas Neue", 30))
        label_subrutinas.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Menú desplegable
        menu_desplegable = ctk.CTkOptionMenu(self.frame_central,
                                             values=["Rutina 1", "Rutina 2", "Rutina 3", "Rutina 4"],
                                             font=("Bebas Neue", 30),
                                             width=600, height=30,
                                             command=self.optionmenu_callback)
        menu_desplegable.grid(row=1, column=0, padx=20, pady=20, sticky="nw")

        # Label número de repeticiones
        label_numero_repeticiones = ctk.CTkLabel(self.frame_numero_repeticiones,
                                                 text="Número de repeticiones de subrutina",
                                                 font=("Bebas Neue", 30))
        label_numero_repeticiones.grid(row=0, column=1, padx=50, pady=20, sticky="nsew")

        # Entrada numérica
        entrada_numero = ctk.CTkEntry(self.frame_spinner, textvariable=self.numero_var,
                                      width=120, justify="center")
        entrada_numero.grid(row=0, column=0, padx=20, pady=20)

        # Botón aumentar
        boton_up = ctk.CTkButton(self.frame_spinner, text="▲", width=110, command=self.aumentar)
        boton_up.grid(row=0, column=1, padx=2, pady=20)

        # Botón disminuir
        boton_down = ctk.CTkButton(self.frame_spinner, text="▼", width=110, command=self.disminuir)
        boton_down.grid(row=0, column=2, padx=2, pady=20)

        # Botón ejecutar
        boton_ejecutar = ctk.CTkButton(self.frame_boton_ejecutar, text="Ejecutar",
                                       font=("Bebas Neue", 30),
                                       width=70, height=30,
                                       corner_radius=13,
                                       command=self.ejecutar_rutina)
        boton_ejecutar.grid(row=0, column=2, padx=2, pady=2)

        # Boton detener la ejecucion
        boton_detener_subrutina = ctk.CTkButton(self.frame_boton_ejecutar, text="Detener",
                                       font=("Bebas Neue", 30),
                                       width=70, height=30,
                                       corner_radius=13,
                                       command=self.ejecutar_rutina)
        boton_detener_subrutina.grid(row=0, column=3, padx=2, pady=2)



"""se crea la app"""
if __name__ == "__main__":
    app = ModoAutomata()