"""
modo_automatico.py
------------------

Módulo que implementa la ventana "Modo Automático" de la interfaz
del brazo robótico. Permite:

- Seleccionar rutinas preprogramadas.
- Establecer número de repeticiones.
- Ejecutar la rutina en Arduino.
- Reproducir un video asociado a cada rutina.
- Detectar la finalización de la rutina mediante lectura de la respuesta del Arduino.

Se integra con `ArduinoDetector` para manejar la comunicación serial.
Utiliza CustomTkinter para la interfaz y OpenCV/Pillow para mostrar video.

Esta ventana se ejecuta como una CTkToplevel, independiente de la ventana principal.

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
import tkinter.messagebox as mbox
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from hardware.arduino_detector import ArduinoDetector
import serial
import time


class ModoAutomatico(ctk.CTkToplevel):
    """
    Ventana de control automático del brazo robótico.

    Parámetros
    ----------
    parent : widget CTk
        Ventana padre desde la cual se invoca esta subventana.

    detector : ArduinoDetector
        Instancia encargada de detectar, abrir y comunicarse con Arduino.

    volver_callback : function, opcional
        Función ejecutada al volver al menú principal.
    """

    def __init__(self, parent, detector, volver_callback=None):
        super().__init__(parent)

        # Referencias externas
        self.parent = parent
        self.detector = detector
        self.volver_callback = volver_callback

        # Estado interno
        self.revisando_conexion = False  # Control de reconexión (si se usa)
        self.rutina_activa = False  # True mientras Arduino ejecuta una rutina
        self.primera_ejecucion = True  # Delay especial de 4s la primera vez

        # ------------------------------
        # Configuración general ventana
        # ------------------------------
        self.title("Modo Automático")
        self.state("zoomed")
        self.minsize(1366, 768)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_completamente)

        # Variables de control UI
        self.subrutina_elegida = ctk.StringVar(value="Rutina 1")
        self.descripcion_subrutina_elegida = ctk.StringVar(
            value="Seleccione una rutina para ver la descripción"
        )
        self.numero_var = ctk.IntVar(value=0)

        # Mapa de rutinas con sus videos asociados
        self.videos = {
            "Rutina 1": r"videos\rutina1-cap.mp4",
            "Rutina 2": r"videos\rutina2-cap.mp4",
            "Rutina 3": r"videos\rutina3-cap.mp4",
            "Rutina 4": r"videos\rutina4-cap.mp4",
        }

        self.cap = None  # Capturador de video
        self.after_id = None  # Para cancelar ciclo de actualización de frames

        # Layout de la ventana
        self._crear_layout_base()

        # Widgets principales
        self.crear_widgets()

        # Iniciar con la primera rutina seleccionada
        self.optionmenu_callback("Rutina 1")

    # ============================================================
    # LAYOUT GENERAL Y WIDGETS
    # ============================================================

    def _crear_layout_base(self):
        """Crea la estructura principal de filas/columnas del layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Frame central que contiene todo excepto el botón Volver
        self.frame_central = ctk.CTkFrame(self)
        self.frame_central.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(6):
            self.frame_central.grid_rowconfigure(i, weight=1)

        self.frame_central.grid_columnconfigure(0, weight=1, uniform="col")
        self.frame_central.grid_columnconfigure(1, weight=1, uniform="col")

        # Frame inferior con el botón Volver
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

        # Frame de video (columna derecha grande)
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

        # Subframes columna izquierda
        self.frame_descripcion = ctk.CTkFrame(
            self.frame_central, fg_color="transparent"
        )
        self.frame_descripcion.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.frame_descripcion.grid_rowconfigure(0, weight=1)
        self.frame_descripcion.grid_columnconfigure(0, weight=1)

        self.frame_numero_repeticiones = ctk.CTkFrame(self.frame_central, height=100)
        self.frame_numero_repeticiones.grid(
            row=3, column=0, padx=10, pady=10, sticky="nsew"
        )

        self.frame_spinner = ctk.CTkFrame(self.frame_central, fg_color="transparent")
        self.frame_spinner.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")

        self.frame_boton_ejecutar = ctk.CTkFrame(
            self.frame_central, fg_color="transparent"
        )
        self.frame_boton_ejecutar.grid(row=5, column=0, padx=20, pady=10, sticky="nsew")

    def crear_widgets(self):
        """Crea todos los widgets visibles del modo automático."""
        # ---- Título ----
        label_subrutinas = ctk.CTkLabel(
            self.frame_central,
            text="Menú de \n subrutinas pre-programadas",
            font=("Bebas Neue", 40),
        )
        label_subrutinas.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # ---- Menú desplegable de rutinas ----
        menu_desplegable = ctk.CTkOptionMenu(
            self.frame_central,
            values=["Rutina 1", "Rutina 2", "Rutina 3", "Rutina 4"],
            font=("Bebas Neue", 40),
            height=60,
            command=self.optionmenu_callback,
        )
        menu_desplegable.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # ---- Caja de descripción ----
        self.cajaTexto = ctk.CTkTextbox(
            self.frame_descripcion,
            corner_radius=13,
            height=185,
            font=("Arial", 16),
        )
        self.cajaTexto.grid(row=0, column=0, sticky="nsew")
        self.cajaTexto.insert("0.0", self.descripcion_subrutina_elegida.get())
        self.cajaTexto.configure(state="disabled")

        # ---- Título: repeticiones ----
        label_numero_repeticiones = ctk.CTkLabel(
            self.frame_numero_repeticiones,
            text="Número de repeticiones de subrutina",
            font=("Bebas Neue", 30),
        )
        label_numero_repeticiones.grid(
            row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew"
        )

        # ---- Spinner numérico ----
        self.frame_spinner.grid_rowconfigure(0, weight=1)
        for col in range(3):
            self.frame_spinner.grid_columnconfigure(col, weight=1)

        self.label_numero = ctk.CTkLabel(
            self.frame_spinner,
            textvariable=self.numero_var,
            font=("Bebas Neue", 25),
            width=120,
            height=40,
            anchor="center",
            corner_radius=10,
        )
        self.label_numero.grid(row=0, column=0, sticky="nsew", padx=5)

        boton_up = ctk.CTkButton(
            self.frame_spinner, text="▲", height=40, command=self.aumentar
        )
        boton_up.grid(row=0, column=1, sticky="nsew", padx=5)

        boton_down = ctk.CTkButton(
            self.frame_spinner, text="▼", height=40, command=self.disminuir
        )
        boton_down.grid(row=0, column=2, sticky="nsew", padx=5)

        # ---- Botones ejecutar / detener ----
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
        self.boton_ejecutar.grid(row=0, column=1, sticky="nsew", padx=5)

        boton_detener = ctk.CTkButton(
            self.frame_boton_ejecutar,
            text="Detener",
            font=("Bebas Neue", 30),
            corner_radius=13,
            height=60,
            command=self.detener_rutina,
        )
        boton_detener.grid(row=0, column=2, sticky="nsew", padx=5)

    # ============================================================
    # MANEJO DE RUTINAS
    # ============================================================

    def optionmenu_callback(self, choice):
        """
        Se ejecuta cuando se selecciona una rutina del menú desplegable.
        - Actualiza la descripción.
        - Detiene el video previo.
        - Reproduce el video de la nueva rutina.
        """
        self.subrutina_elegida.set(choice)
        self.mostrar_informacion_subrutina(choice)

        # Reset del video actual
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

        # Reproducir video asociado
        if ruta := self.videos.get(choice):
            self.reproducir_video(ruta)

    def mostrar_informacion_subrutina(self, choice):
        """Actualiza la descripción en la caja de texto según la rutina seleccionada."""
        textos = {
            "Rutina 1": "Rutina de prueba de pinza:\n● Baja hombro\n● Cierra/abre pinza\n● Sube hombro.",
            "Rutina 2": "Desapilar:\n● Mover a pila.\n● Preparar pinza.\n● Tomar elemento.",
            "Rutina 3": "Apilar:\n● Tomar elemento.\n● Llevar a pila.\n● Colocar elemento.",
            "Rutina 4": "Forma arco/cuadrado:\n● Trazo.\n● Cierra al bajar.\n● Abre al subir.",
        }

        texto = textos.get(choice, "No hay información disponible")

        self.descripcion_subrutina_elegida.set(texto)
        self.cajaTexto.configure(state="normal")
        self.cajaTexto.delete("0.0", "end")
        self.cajaTexto.insert("0.0", texto)
        self.cajaTexto.configure(state="disabled")

    def aumentar(self):
        """Incrementa el número de repeticiones (máximo 5)."""
        if self.numero_var.get() < 5:
            self.numero_var.set(self.numero_var.get() + 1)

    def disminuir(self):
        """Disminuye el número de repeticiones (mínimo 0)."""
        if self.numero_var.get() > 0:
            self.numero_var.set(self.numero_var.get() - 1)

    def ejecutar_rutina(self):
        """
        Envía al Arduino el comando para ejecutar una rutina.
        Aplica un delay de 4000ms solo la primera vez.
        Inicia un bucle de verificación periódica para saber
        si Arduino terminó o si ocurre un timeout.
        """
        rutina_str = self.subrutina_elegida.get()
        repeticiones = self.numero_var.get()

        # Convertir "Rutina X" → X
        try:
            rutina = int(rutina_str.split()[-1])
        except ValueError:
            print("Formato inválido de rutina:", rutina_str)
            return

        # Bloquear botón para evitar múltiples envíos
        self.boton_ejecutar.configure(state="disabled")

        def enviar_comando():
            """Función interna que envía el comando al Arduino."""
            exito = self.detector.enviar_rutina(rutina, repeticiones)
            if not exito:
                mbox.showinfo(
                    "Error de conexion con Arduino",
                    "No fue posible iniciar la rutina.",
                    parent=self,
                )
                self.boton_ejecutar.configure(state="normal")
                return

            # Tiempo límite
            timeout_segundos = 80
            tiempo_inicio = time.time()
            self.rutina_activa = True

            def revisar_respuesta():
                """Revisa periódicamente si Arduino terminó la rutina."""
                if not self.rutina_activa:
                    return

                try:
                    respuesta = self.detector.leer_respuesta()
                except Exception as e:
                    self.rutina_activa = False
                    mbox.showerror(
                        "Error de comunicación",
                        f"No se pudo leer la respuesta de Arduino.\n{e}",
                        parent=self,
                    )
                    self.boton_ejecutar.configure(state="normal")
                    return

                # Finalización
                if respuesta == "Rutina completada":
                    self.rutina_activa = False
                    mbox.showinfo(
                        "Rutina completada",
                        f"{rutina_str} finalizada correctamente.",
                        parent=self,
                    )
                    self.boton_ejecutar.configure(state="normal")
                    return

                # Timeout
                if time.time() - tiempo_inicio > timeout_segundos:
                    self.rutina_activa = False
                    mbox.showinfo("Timeout", "Arduino no respondió a tiempo.")
                    self.boton_ejecutar.configure(state="normal")
                    return

                # Seguir revisando
                self.after(100, revisar_respuesta)

            # Iniciar revisión
            self.after(100, revisar_respuesta)

        # Delay especial solo primera vez
        if self.primera_ejecucion:
            self.primera_ejecucion = False
            self.after(4000, enviar_comando)
        else:
            enviar_comando()

    def detener_rutina(self):
        """
        Envía el comando para detener la rutina en ejecución (rutina 0).
        Solo se permite detener si el botón Ejecutar está deshabilitado,
        lo cual indica que una rutina está corriendo.
        """
        if self.boton_ejecutar.cget("state") == "normal":
            return

        exito = self.detector.enviar_rutina(0, 0)
        if not exito:
            print("Error enviando comando de detención.")
            return

        def revisar_detencion():
            """Espera la confirmación 'Rutina detenida' desde Arduino."""
            respuesta = self.detector.leer_respuesta()
            if respuesta == "Rutina detenida":
                self.boton_ejecutar.configure(state="normal")
            else:
                self.after(100, revisar_detencion)

        revisar_detencion()

    # ============================================================
    # MANEJO DE VIDEO
    # ============================================================

    def reproducir_video(self, ruta_video):
        """
        Reproduce un video en loop dentro del label `self.label_video`.
        Usa OpenCV para leer frames y Pillow para mostrarlos en Tkinter.
        """
        # Cancelar ciclo anterior
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        # Cerrar video anterior
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

        self.cap = cv2.VideoCapture(ruta_video)
        if not self.cap.isOpened():
            print("No se pudo abrir el video:", ruta_video)
            return

        def mostrar_frame():
            """Lee un frame, lo escala al tamaño del contenedor y lo muestra."""
            ret, frame = self.cap.read()

            # Loop infinito del video
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return

            # Obtener tamaño del label
            w_label = self.label_video.winfo_width()
            h_label = self.label_video.winfo_height()

            if w_label <= 1 or h_label <= 1:
                self.after_id = self.after(100, mostrar_frame)
                return

            # Escala manteniendo relación de aspecto
            h_vid, w_vid = frame.shape[:2]
            escala = min(w_label / w_vid, h_label / h_vid)
            nuevo_w = int(w_vid * escala)
            nuevo_h = int(h_vid * escala)

            frame = cv2.resize(frame, (nuevo_w, nuevo_h))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Fondo negro centrado
            fondo = Image.new("RGB", (w_label, h_label), color=(0, 0, 0))
            fondo.paste(
                Image.fromarray(frame),
                ((w_label - nuevo_w) // 2, (h_label - nuevo_h) // 2),
            )

            img_final = ImageTk.PhotoImage(fondo)
            self.label_video.configure(image=img_final)
            self.label_video.image = img_final

            self.after_id = self.after(30, mostrar_frame)

        mostrar_frame()

    # ============================================================
    # CIERRE Y LIMPIEZA
    # ============================================================

    def volver_al_menu(self):
        """Ejecuta el callback de retorno y destruye esta ventana."""
        if self.volver_callback:
            self.volver_callback()
        self.destroy()

    def cerrar_completamente(self):
        """Limpia video, rutina y detector antes de cerrar la ventana."""
        try:
            self.detener_rutina()
        except:
            pass

        try:
            if self.after_id:
                self.after_cancel(self.after_id)
        except:
            pass

        try:
            if self.detector:
                self.detector.cerrar()
        except:
            pass

        if self.volver_callback:
            self.volver_callback()

        self.destroy()


if __name__ == "__main__":
    # Para pruebas manuales del archivo
    root = ctk.CTk()
    root.title("Ventana principal simulada")
    root.after(100, lambda: root.state("zoomed"))

    def mostrar_ventana_principal():
        root.deiconify()
        root.after(100, lambda: root.state("zoomed"))

    app = ModoAutomatico(root, detector=None, volver_callback=mostrar_ventana_principal)
    root.withdraw()
    root.mainloop()
