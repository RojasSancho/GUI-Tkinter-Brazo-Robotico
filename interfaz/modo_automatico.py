import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2


class ModoAutomatico(ctk.CTkToplevel):
    def __init__(self, parent, volver_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.volver_callback = volver_callback

        # ------------------------------
        # Configuración de la ventana
        # ------------------------------
        self.title("Modo Automático")
        self.state("zoomed")
        self.minsize(1366, 768)
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

        # ------------------------------
        # Frame central
        # ------------------------------
        self.frame_central = ctk.CTkFrame(self)
        self.frame_central.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configuración de filas y columnas
        for i in range(6):
            self.frame_central.grid_rowconfigure(i, weight=1)
        self.frame_central.grid_columnconfigure(0, weight=1, uniform="col")
        self.frame_central.grid_columnconfigure(1, weight=1, uniform="col")

        # ------------------------------
        # Frames principales de la columna izquierda
        # ------------------------------
        # Fila 2: descripción
        self.frame_descripcion = ctk.CTkFrame(
            self.frame_central, fg_color="transparent"
        )
        self.frame_descripcion.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.frame_descripcion.grid_rowconfigure(0, weight=1)
        self.frame_descripcion.grid_columnconfigure(0, weight=1)

        # Fila 3: número de repeticiones
        self.frame_numero_repeticiones = ctk.CTkFrame(self.frame_central, height=100)
        self.frame_numero_repeticiones.grid(
            row=3, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.frame_numero_repeticiones.grid_columnconfigure(0, weight=1)

        # Fila 4: spinner
        self.frame_spinner = ctk.CTkFrame(self.frame_central, fg_color="transparent")
        self.frame_spinner.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")

        # Fila 5: botones ejecutar y detener
        self.frame_boton_ejecutar = ctk.CTkFrame(
            self.frame_central, fg_color="transparent"
        )
        self.frame_boton_ejecutar.grid(row=5, column=0, padx=20, pady=10, sticky="nsew")

        # ------------------------------
        # Frame inferior con botón volver
        # ------------------------------
        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.frame_inferior.grid_columnconfigure(0, weight=1)
        self.frame_inferior.grid_columnconfigure(1, weight=0)

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
        # Widgets columna izquierda
        # ------------------------------
        self.crear_widgets()

        # ------------------------------
        # Frame de video (columna derecha)
        # ------------------------------
        self.frame_video_player = ctk.CTkFrame(
            self.frame_central, height=400, fg_color="white"
        )
        self.frame_video_player.grid(
            row=1, column=1, rowspan=4, padx=10, pady=20, sticky="nsew"
        )

        self.label_video = ctk.CTkLabel(
            self.frame_video_player, text="", fg_color="black"
        )
        self.label_video.pack(expand=True, fill="both")

        self.reproducir_video_prueba(r"videos\VideoTemu.mp4")

    # ------------------------------
    # Métodos de control
    # ------------------------------
    def volver_al_menu(self):
        if self.volver_callback:
            self.volver_callback()
        self.destroy()

    def optionmenu_callback(self, choice):
        self.subrutina_elegida.set(choice)
        self.mostrar_informacion_subrutina(choice)

    def mostrar_informacion_subrutina(self, choice):
        textos = {
            "Rutina 1": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeo",
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
        self.numero_var.set(max(0, self.numero_var.get() - 1))

    def ejecutar_rutina(self):
        print(
            f"Se ejecutará la: {self.subrutina_elegida.get()} {self.numero_var.get()} veces"
        )

    def detener_rutina(self):
        print(f"Se detendrá la: {self.subrutina_elegida.get()}")

    # ------------------------------
    # Widgets
    # ------------------------------
    def crear_widgets(self):
        # Fila 0: título
        label_subrutinas = ctk.CTkLabel(
            self.frame_central,
            text="Menú de \n subrutinas pre-programadas",
            font=("Bebas Neue", 30),
        )
        label_subrutinas.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Fila 1: menú desplegable
        menu_desplegable = ctk.CTkOptionMenu(
            self.frame_central,
            values=["Rutina 1", "Rutina 2", "Rutina 3", "Rutina 4"],
            font=("Bebas Neue", 30),
            height=70,
            command=self.optionmenu_callback,
        )
        menu_desplegable.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Caja de texto descripción
        self.cajaTexto = ctk.CTkTextbox(self.frame_descripcion, corner_radius=0)
        self.cajaTexto.grid(row=0, column=0, sticky="nsew")
        self.cajaTexto.insert("0.0", self.descripcion_subrutina_elegida.get())

        # Label número de repeticiones
        label_numero_repeticiones = ctk.CTkLabel(
            self.frame_numero_repeticiones,
            text="Número de repeticiones de subrutina",
            font=("Bebas Neue", 30),
        )
        label_numero_repeticiones.grid(
            row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew"
        )

        # Entrada numérica y botones del spinner
        self.frame_spinner.grid_rowconfigure(0, weight=1)
        for col in range(3):
            self.frame_spinner.grid_columnconfigure(col, weight=1)

        entrada_numero = ctk.CTkEntry(
            self.frame_spinner,
            textvariable=self.numero_var,
            width=120,
            height=40,
            justify="center",
        )
        entrada_numero.grid(row=0, column=0, sticky="nsew", padx=5, pady=0)

        boton_up = ctk.CTkButton(
            self.frame_spinner, text="▲", height=40, command=self.aumentar
        )
        boton_up.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)

        boton_down = ctk.CTkButton(
            self.frame_spinner, text="▼", height=40, command=self.disminuir
        )
        boton_down.grid(row=0, column=2, sticky="nsew", padx=5, pady=0)

        # Botones ejecutar y detener
        self.frame_boton_ejecutar.grid_rowconfigure(0, weight=1)
        for col in range(4):
            self.frame_boton_ejecutar.grid_columnconfigure(col, weight=1)

        boton_ejecutar = ctk.CTkButton(
            self.frame_boton_ejecutar,
            text="Ejecutar",
            font=("Bebas Neue", 30),
            corner_radius=13,
            height=60,
            command=self.ejecutar_rutina,
        )
        boton_ejecutar.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)

        boton_detener_subrutina = ctk.CTkButton(
            self.frame_boton_ejecutar,
            text="Detener",
            font=("Bebas Neue", 30),
            corner_radius=13,
            height=60,
            command=self.detener_rutina,
        )
        boton_detener_subrutina.grid(row=0, column=2, sticky="nsew", padx=5, pady=0)

    # ------------------------------
    # Reproducción de video
    # ------------------------------
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

            fondo = Image.new("RGB", (ancho_label, alto_label), color=(0, 0, 0))
            fondo.paste(
                Image.fromarray(frame),
                ((ancho_label - nuevo_ancho) // 2, (alto_label - nuevo_alto) // 2),
            )

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
