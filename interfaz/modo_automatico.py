import tkinter as tk
import tkinter.messagebox as mbox
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from hardware.arduino_detector import ArduinoDetector
import serial
import time


class ModoAutomatico(ctk.CTkToplevel):
    def __init__(self, parent, detector, volver_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.volver_callback = volver_callback
        self.revisando_conexion = False
        self.detector = detector
        self.rutina_activa = False
        self.primera_ejecucion = True  # variable de control

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
        self.subrutina_elegida = ctk.StringVar(value="Rutina 1")
        self.descripcion_subrutina_elegida = ctk.StringVar(
            value="Seleccione una rutina para ver la descripción"
        )
        self.numero_var = ctk.IntVar(value=0)
        self.videos = {
            "Rutina 1": r"videos\rutina1.mp4",
            "Rutina 2": r"videos\rutina2.mp4",
            "Rutina 3": r"videos\rutina3.mp4",
            "Rutina 4": r"videos\rutina4.mp4",
        }

        self.cap = None

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

        # --- Selección inicial predeterminada ---
        self.optionmenu_callback("Rutina 1")

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

        # Detener video actual si hay uno

        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

        if ruta_video := self.videos.get(choice):
            self.reproducir_video(ruta_video)

    def mostrar_informacion_subrutina(self, choice):
        textos = {
            "Rutina 1": "Rutina de prueba de pinza: \n● Realiza un movimiento hacia abajo del servo de hombro\n● Cierra y abre la pinza\n● Vuelve a subir el hombro.",
            "Rutina 2": "Rutina para desapilar:\n● Se mueve al punto donde se encuentran los elementos apilados.\n● Prepara la posición de la pinza para tomar el siguiente elemento de la pila.\n● Cierra la pinza y retira el elemento de la pila. ",
            "Rutina 3": "Rutina para apilar:\n● Prepara la posición de la pinza para tomar un nuevo elemento a apilar.\n● Cierra la pinza y realiza movimiento hacia la pila.\n● Coloca el siguiente elemento de la pila.",
            "Rutina 4": "Rutina en forma de arco: \n● Realiza una forma de arco o cuadrado.\n● Cierra la pinza cuando baja y la abre cuando sube.",
        }
        texto = textos.get(choice, "No hay información disponible")
        self.descripcion_subrutina_elegida.set(texto)
        self.cajaTexto.configure(state="normal")
        self.cajaTexto.delete("0.0", "end")
        self.cajaTexto.insert("0.0", texto)
        self.cajaTexto.configure(state="disabled")

    def aumentar(self):
        if self.numero_var.get() < 5:
            self.numero_var.set(self.numero_var.get() + 1)

    def disminuir(self):
        if self.numero_var.get() > 0:
            self.numero_var.set(self.numero_var.get() - 1)

    def ejecutar_rutina(self):
        # Obtener valores del GUI
        rutina_str = self.subrutina_elegida.get()
        repeticiones = self.numero_var.get()

        try:
            rutina = int(rutina_str.split()[-1])
        except ValueError:
            print(f"Formato inválido de la rutina: {rutina_str}")
            return

        # Bloquear botón ejecutar
        self.boton_ejecutar.configure(state="disabled")

        # Función que realmente envía el comando al Arduino
        def enviar_comando():
            exito = self.detector.enviar_rutina(rutina, repeticiones)
            if not exito:
                print("No fue posible enviar comando.")
                mbox.showinfo(
                    "Error de conexion con Arduino",
                    "No fue posible iniciar la rutina. Revise la conexion fisica.",
                    parent=self,
                )
                self.boton_ejecutar.configure(state="normal")
                return
            print("Comando enviado correctamente.")

            # Guardar tiempo de inicio de rutina y timeout maximo (ms)
            tiempo_inicio = time.time()
            timeout_segundos = 80

            # Función interna para revisar respuesta periódicamente
            def revisar_respuesta():
                if not self.rutina_activa:
                    return

                try:
                    respuesta = self.detector.leer_respuesta()
                except Exception as e:
                    self.rutina_activa = False
                    print("ERROR: Comunicación con Arduino falló:", e)
                    mbox.showerror(
                        "Error de comunicación",
                        f"No se pudo leer la respuesta de Arduino.\nDetalle: {e}",
                        parent=self,
                    )
                    self.boton_ejecutar.configure(state="normal")
                    return

                tiempo_transcurrido = time.time() - tiempo_inicio

                if respuesta == "Rutina completada":
                    self.rutina_activa = False
                    print(f"{rutina_str} completada por Arduino.")
                    mbox.showinfo(
                        "Rutina completada",
                        f"Las repeticiones de {rutina_str} han sido completadas.",
                        parent=self,
                    )
                    self.boton_ejecutar.configure(state="normal")
                elif tiempo_transcurrido > timeout_segundos:
                    self.rutina_activa = False
                    print("ERROR: Timeout. Arduino no respondió a tiempo.")
                    mbox.showinfo(
                        "Timeout", "ERROR: Arduino no respondió a tiempo.", parent=self
                    )
                    self.boton_ejecutar.configure(state="normal")
                else:
                    self.after(100, revisar_respuesta)

            # Iniciar la revisión
            self.rutina_activa = True
            self.after(100, revisar_respuesta)

        # --- Delay solo la primera vez ---
        if self.primera_ejecucion:
            self.primera_ejecucion = False
            print("Primera ejecución: esperando 4 segundos antes de enviar")
            self.after(4000, enviar_comando)
        else:
            enviar_comando()

    def detener_rutina(self):
        # Solo se envía si la rutina estaba en ejecución (botón ejecutar deshabilitado)
        if self.boton_ejecutar.cget("state") == "normal":
            return  # No hay rutina activa, no hacer nada

        # Envia comando de detencion al Arduino
        exito = self.detector.enviar_rutina(0, 0)  # rutina 0 significa detener

        if not exito:
            print("No fue posible enviar comando de detención.")
            return

        print("Comando de detención enviado correctamente.")

        # Función interna para revisar respuesta periódicamente

        def revisar_detencion():
            respuesta = self.detector.leer_respuesta()
            if respuesta == "Rutina detenida":
                print("Arduino confirma detención de la rutina.")
                self.boton_ejecutar.configure(state="normal")
            else:
                self.after(100, revisar_detencion)

        revisar_detencion()

    # ------------------------------
    # Widgets
    # ------------------------------
    def crear_widgets(self):
        # Fila 0: título
        label_subrutinas = ctk.CTkLabel(
            self.frame_central,
            text="Menú de \n subrutinas pre-programadas",
            font=("Bebas Neue", 40),
        )
        label_subrutinas.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Fila 1: menú desplegable
        menu_desplegable = ctk.CTkOptionMenu(
            self.frame_central,
            values=["Rutina 1", "Rutina 2", "Rutina 3", "Rutina 4"],
            font=("Bebas Neue", 40),
            height=60,
            command=self.optionmenu_callback,
        )
        menu_desplegable.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Caja de texto descripción
        self.cajaTexto = ctk.CTkTextbox(
            self.frame_descripcion,
            corner_radius=13,
            height=185,
            font=("Arial", 16),
        )
        self.cajaTexto.grid(row=0, column=0, sticky="nsew")
        self.cajaTexto.insert("0.0", self.descripcion_subrutina_elegida.get())
        self.cajaTexto.configure(state="disabled")

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

        self.label_numero = ctk.CTkLabel(
            self.frame_spinner,
            textvariable=self.numero_var,
            font=("Bebas Neue", 25),
            # text_color="black",
            width=120,
            height=40,
            anchor="center",
            corner_radius=10,
            # fg_color="#CCCCCC",
        )
        self.label_numero.grid(row=0, column=0, sticky="nsew", padx=5, pady=0)

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

        self.boton_ejecutar = ctk.CTkButton(
            self.frame_boton_ejecutar,
            text="Ejecutar",
            font=("Bebas Neue", 30),
            corner_radius=13,
            height=60,
            command=self.ejecutar_rutina,
        )
        self.boton_ejecutar.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)

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
    def reproducir_video(self, ruta_video):
        # Cancelar ciclo anterior de actualización de frames
        if hasattr(self, "after_id") and self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        # Cerrar video anterior si hay uno abierto
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

        self.cap = cv2.VideoCapture(ruta_video)

        if not self.cap.isOpened():
            print("No se pudo abrir el video:", ruta_video)
            return

        def mostrar_frame():
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return  # si sigue fallando, detiene el bucle

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

            # Guardar el id del ciclo para poder cancelarlo después
            self.after_id = self.after(24, mostrar_frame)

        mostrar_frame()

    def cerrar_completamente(self):
        # Detener rutina que se encuentre activa
        try:
            self.detener_rutina()
        except Exception:
            pass

        # Detener la reproducción del video
        try:
            if hasattr(self, "after_id") and self.after_id:
                self.after_cancel(self.after_id)
        except:
            pass

        # Cerrar detector correctamente
        try:
            if hasattr(self, "detector") and self.detector:
                self.detector.cerrar()
        except Exception:
            pass

        # Volver al menú principal en vez de destruir parent
        if self.volver_callback:
            self.volver_callback()

        self.destroy()


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
