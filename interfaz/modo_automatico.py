import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from customtkinter import CTkImage


class ModoAutomatico(ctk.CTkToplevel):
    def __init__(self, parent, volver_callback=None):
        super().__init__(parent)
        self.parent = parent  # ventana principal
        self.volver_callback = volver_callback

        self.title("Modo Automático")
        self.state("zoomed")
        self.minsize(1366, 768)

        # Manejar cierre con la X
        self.protocol("WM_DELETE_WINDOW", self.cerrar_completamente)

        # ------------------------------
        # Variables
        # ------------------------------
        self.subrutina_elegida = ctk.StringVar(value="")
        self.descripcion_subrutina_elegida = ctk.StringVar(
            value="Seleccione una rutina para ver la descripción"
        )
        self.numero_var = ctk.IntVar(value=0)
        self.videos = {
            "Rutina 1": "video1.mp4",
            "Rutina 2": "video2.mp4",
            "Rutina 3": "video3.mp4",
            "Rutina 4": "video4.mp4",
        }

        # ------------------------------
        # Layout principal
        # ------------------------------
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Frame central
        self.frame_central = ctk.CTkFrame(self)
        self.frame_central.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_central.grid_rowconfigure(0, weight=0)
        self.frame_central.grid_rowconfigure(1, weight=0)
        self.frame_central.grid_rowconfigure(2, weight=0)
        self.frame_central.grid_rowconfigure(3, weight=0)
        self.frame_central.grid_rowconfigure(4, weight=1)
        self.frame_central.grid_columnconfigure(1, weight=1)
        for i in range(1, 5):
            self.frame_central.grid_rowconfigure(i, weight=1)

        # Frame descripción
        self.frame_descripcion = ctk.CTkFrame(
            self.frame_central, width=340, height=200, fg_color="white"
        )
        self.frame_descripcion.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Frame número repeticiones
        self.frame_numero_repeticiones = ctk.CTkFrame(
            self.frame_central, width=340, height=100
        )
        self.frame_numero_repeticiones.grid(
            row=3, column=0, padx=10, pady=10, sticky="nsew"
        )

        # Frame spinner
        self.frame_spinner = ctk.CTkFrame(self.frame_central, fg_color="transparent")
        self.frame_spinner.grid(row=4, column=0, padx=20, pady=20, sticky="n")

        # Frame botón ejecutar y detener
        self.frame_boton_ejecutar = ctk.CTkFrame(
            self.frame_central, fg_color="transparent"
        )
        self.frame_boton_ejecutar.grid(row=5, column=0, padx=20, pady=20, sticky="n")

        # ------------------------------
        # Frame inferior con botón volver
        # ------------------------------
        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.frame_inferior.grid_columnconfigure(0, weight=1)
        self.frame_inferior.grid_columnconfigure(1, weight=0)

        # Botón volver al menú principal
        boton_volver = ctk.CTkButton(
            self.frame_inferior,
            text="Volver al menú principal",
            font=("Bebas Neue", 25),
            width=220,
            height=40,
            corner_radius=10,
            command=self.volver_al_menu,
        )
        boton_volver.grid(row=0, column=1, sticky="e")

        # ------------------------------
        # Widgets de selección y control
        # ------------------------------
        self.crear_widgets()

        # Frame donde se mostrará el video
        self.frame_video_player = ctk.CTkFrame(
            self.frame_central, width=685, height=400, fg_color="white"
        )
        self.frame_video_player.grid(
            row=1, column=1, rowspan=4, padx=10, pady=20, sticky="nsew"
        )

        # Label que contendrá cada frame
        self.label_video = ctk.CTkLabel(
            self.frame_video_player, text="", fg_color="black"
        )
        self.label_video.pack(expand=True, fill="both")

        self.reproducir_video_prueba(r"videos\prueba2.mp4")

    # ------------------------------
    # Métodos
    # ------------------------------
    def volver_al_menu(self):
        if self.volver_callback:
            self.volver_callback()  # Llama a la función que muestra la ventana principal
        self.destroy()  # Cierra esta ventana

    def optionmenu_callback(self, choice):
        self.subrutina_elegida.set(choice)
        self.mostrar_informacion_subrutina(choice)
        # self.cambiar_video(choice)  # Si tienes videos activos

    def mostrar_informacion_subrutina(self, choice):
        textos = {
            "Rutina 1": "Rutina 1 realiza estas acciones",
            "Rutina 2": "Rutina 2 realiza estas acciones",
            "Rutina 3": "Rutina 3 realiza estas acciones",
            "Rutina 4": "Rutina 4 realiza estas acciones",
        }
        texto = textos.get(choice, "No hay información disponible")
        self.descripcion_subrutina_elegida.set(texto)
        self.cajaTexto.delete("0.0", "end")
        self.cajaTexto.insert("0.0", texto)

    def aumentar(self):
        self.numero_var.set(self.numero_var.get() + 1)

    def disminuir(self):
        valor = max(0, self.numero_var.get() - 1)
        self.numero_var.set(valor)

    def ejecutar_rutina(self):
        print(
            f"Se ejecutará la: {self.subrutina_elegida.get()} {self.numero_var.get()} veces"
        )

    def detener_rutina(self):
        print(f"Se detendrá la: {self.subrutina_elegida.get()}")

    def crear_widgets(self):
        # Label menú
        label_subrutinas = ctk.CTkLabel(
            self.frame_central,
            text="Menú \n de subrutinas pre-programadas",
            font=("Bebas Neue", 30),
        )
        label_subrutinas.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Menú desplegable
        menu_desplegable = ctk.CTkOptionMenu(
            self.frame_central,
            values=["Rutina 1", "Rutina 2", "Rutina 3", "Rutina 4"],
            font=("Bebas Neue", 30),
            width=600,
            height=30,
            command=self.optionmenu_callback,
        )
        menu_desplegable.grid(row=1, column=0, padx=20, pady=20, sticky="nw")

        # Caja de texto con la descripción
        self.cajaTexto = ctk.CTkTextbox(
            self.frame_descripcion, width=300, corner_radius=0
        )
        self.cajaTexto.grid(row=0, column=0, sticky="nsew")
        self.cajaTexto.insert("0.0", self.descripcion_subrutina_elegida.get())

        # Label número de repeticiones
        label_numero_repeticiones = ctk.CTkLabel(
            self.frame_numero_repeticiones,
            text="Número de repeticiones de subrutina",
            font=("Bebas Neue", 30),
        )
        label_numero_repeticiones.grid(row=0, column=1, padx=50, pady=20, sticky="nsew")

        # Entrada numérica
        entrada_numero = ctk.CTkEntry(
            self.frame_spinner,
            textvariable=self.numero_var,
            width=120,
            justify="center",
        )
        entrada_numero.grid(row=0, column=0, padx=20, pady=20)

        # Botón aumentar
        boton_up = ctk.CTkButton(
            self.frame_spinner, text="▲", width=110, command=self.aumentar
        )
        boton_up.grid(row=0, column=1, padx=2, pady=20)

        # Botón disminuir
        boton_down = ctk.CTkButton(
            self.frame_spinner, text="▼", width=110, command=self.disminuir
        )
        boton_down.grid(row=0, column=2, padx=2, pady=20)

        # Botón ejecutar
        boton_ejecutar = ctk.CTkButton(
            self.frame_boton_ejecutar,
            text="Ejecutar",
            font=("Bebas Neue", 30),
            width=110,
            height=30,
            corner_radius=13,
            command=self.ejecutar_rutina,
        )
        boton_ejecutar.grid(row=0, column=2, padx=2, pady=2)

        # Botón detener
        boton_detener_subrutina = ctk.CTkButton(
            self.frame_boton_ejecutar,
            text="Detener",
            font=("Bebas Neue", 30),
            width=110,
            height=30,
            corner_radius=13,
            command=self.detener_rutina,
        )
        boton_detener_subrutina.grid(row=0, column=3, padx=2, pady=2)

    def reproducir_video_prueba(self, ruta_video):
        self.cap = cv2.VideoCapture(ruta_video)

        if not self.cap.isOpened():
            print("No se pudo abrir el video:", ruta_video)
            return

        def mostrar_frame():
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()

            self.label_video.update_idletasks()
            ancho_label = self.label_video.winfo_width()
            alto_label = self.label_video.winfo_height()

            if ancho_label <= 1 or alto_label <= 1:
                self.after(100, mostrar_frame)
                return

            alto_video, ancho_video = frame.shape[:2]
            factor_escala = min(ancho_label / ancho_video, alto_label / alto_video)
            nuevo_ancho = int(ancho_video * factor_escala)
            nuevo_alto = int(alto_video * factor_escala)

            frame = cv2.resize(frame, (nuevo_ancho, nuevo_alto))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Crear fondo negro y pegar video centrado
            fondo = Image.new("RGB", (ancho_label, alto_label), color=(0, 0, 0))
            fondo.paste(
                Image.fromarray(frame),
                ((ancho_label - nuevo_ancho) // 2, (alto_label - nuevo_alto) // 2),
            )

            # Convertir a PhotoImage para Tkinter
            img_final = ImageTk.PhotoImage(fondo)

            self.label_video.configure(image=img_final)
            self.label_video.image = img_final

            self.after(30, mostrar_frame)

        mostrar_frame()

    def cerrar_completamente(self):
        self.destroy()
        self.parent.destroy()


# ------------------------------
# Prueba rápida
# ------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Ventana principal simulada")
    root.after(100, lambda: root.state("zoomed"))

    def mostrar_ventana_principal():
        root.deiconify()
        root.after(100, lambda: root.state("zoomed"))

    app = ModoAutomatico(root, volver_callback=mostrar_ventana_principal)
    root.withdraw()
    root.mainloop()
