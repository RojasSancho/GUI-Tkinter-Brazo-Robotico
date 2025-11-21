import tkinter as tk
import customtkinter as ctk
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from hardware.arduino_detector import ArduinoDetector
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


# ------------------------------
#     Clase modo automatico
# ------------------------------
class ModoManual(ctk.CTkToplevel):
    def __init__(self, parent, detector, volver_callback=None):

        """
        L1: altura base, simbolico por que en realida es la base
        L2: longitud primer segmento
        L3: longitud segundo segmento
        largo_pinza: longitud visual de la pinza
        """
        self.L1 = 3
        self.L2 = 5
        self.L3 = 5
        self.largo_pinza = 4

        super().__init__(parent)

        # -----------------------------------
        #  DETECTOR
        # -----------------------------------
        self.detector = detector

        self.volver_callback = volver_callback

        self.title("Modo Manual")
        self.state("zoomed")
        self.minsize(1366, 768)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_completamente)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Frame central
        self.frame_central = ctk.CTkFrame(self)
        self.frame_central.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.frame_central.grid_rowconfigure(0, weight=0)
        self.frame_central.grid_rowconfigure(1, weight=0)
        self.frame_central.grid_rowconfigure(2, weight=1)
        self.frame_central.grid_columnconfigure(0, weight=0)
        self.frame_central.grid_columnconfigure(1, weight=1)

        # Frame de los controles (sliders horizontales)
        self.frame_scroll_control = ctk.CTkFrame(
            self.frame_central, width=340, height=400
        )
        self.frame_scroll_control.grid(
            row=1, column=0, rowspan=3, padx=10, pady=10, sticky="nsew"
        )
        self.frame_scroll_control.grid_columnconfigure(0, weight=100)

        # Permite crecimiento de filas
        for i in range(20):  # muchas filas
            self.frame_scroll_control.grid_rowconfigure(i, weight=1)
            self.frame_scroll_control.grid_columnconfigure(0, weight=1)

        # Frame diagrama (diagrama en 3d)
        self.frame_diagrama = ctk.CTkFrame(self.frame_central)
        self.frame_diagrama.grid(
            row=1, column=1, rowspan=3, padx=10, pady=10, sticky="nsew"
        )

        # Label superior
        label_controles = ctk.CTkLabel(
            self.frame_central,
            text="Controles de Servomotores (grados)",
            font=("Bebas Neue", 30),
        )
        label_controles.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # Label superior
        label_diagrama = ctk.CTkLabel(
            self.frame_central,
            text="Diagrama esqueleto brazo robótico en 3D",
            font=("Bebas Neue", 30),
        )
        label_diagrama.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # ------------------------------
        # Frame inferior del botón volver
        # ------------------------------
        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.frame_inferior.grid_columnconfigure(0, weight=1)
        self.frame_inferior.grid_columnconfigure(1, weight=0)

        # Botón para volver al menu principal
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

        # Crea el grafico y los botones sliders
        self.crear_sliders()
        self.crear_grafico()

    # ------------------------------
    #   Crea los botones slider
    # ------------------------------
    def crear_sliders(self):
        self.slider_vals = {
            "base": ctk.DoubleVar(value=90),
            "brazo": ctk.DoubleVar(value=140),
            "codo": ctk.DoubleVar(value=110),
            "pinza": ctk.DoubleVar(value=90),
        }

        controles = [
            ("Base (0–180°)", "base", 0, 180, "red"),
            ("Brazo (130-170°)", "brazo", 130, 170, "green"),
            ("Codo (110–150°)", "codo", 110, 150, "orange"),
            ("Pinza (0–100%)", "pinza", 0, 180, "blue"),
        ]

        for i, control in enumerate(controles):
            if len(control) == 5:
                texto, varname, mn, mx, color = control

            label = ctk.CTkLabel(
                self.frame_scroll_control,
                text=texto,
                font=("Arial", 16),
                text_color="black",
                fg_color="#e6e6e6",
                corner_radius=6,
            )
            label.grid(row=i * 2, column=0, padx=10, pady=(10, 0), sticky="w")


            # Cada slider envía su valor al Arduino mediante un callback
            slider = ctk.CTkSlider(
                self.frame_scroll_control,
                from_=mn,
                to=mx,
                variable=self.slider_vals[varname],
                command=lambda val, n=varname: self.enviar_y_actualizar(n, val),
                progress_color=color,
                button_color=color,
            )
            slider.grid(row=i * 2 + 1, column=0, padx=10, pady=(0, 10), sticky="ew")

    # Envía el comando al Arduino y actualiza el gráfico
    def enviar_y_actualizar(self, nombre, valor):
        ang = int(float(valor))  # asegura conversión correcta

        # Mapea slider → número de servo
        mapa_servos = {
            "base": 4,
            "brazo": 1,
            "codo": 2,
            "pinza": 3,
        }

        # Envía comando Sa,b al Arduino
        try:
            # -----------------------------
            # Antes: self.parent.enviar_slider
            # Ahora: self.detector.enviar_slider
            # -----------------------------
            self.detector.enviar_slider(mapa_servos[nombre], ang)
        except Exception as e:
            print("Error enviando al Arduino:", e)

        # Actualiza el gráfico después de mover el slider
        self.actualizar_grafico()

    # ------------------------------
    def cinematicas_3d(self, angulo_base, angulo_brazo, angulo_codo):
        """
        Calcula coordenadas 3D de ambos segmentos
        angulo_base: rotación horizontal (°)
        angulo_brazo: elevación primer segmento (°)
        angulo_codo: ángulo del segundo segmento (°)
        """
        angulo_base_radianes = np.radians(angulo_base)
        angulo_brazo_radianes = np.radians(angulo_brazo)
        angulo_codo_radianes = np.radians(angulo_codo)

        # Base vertical
        x0, y0, z0 = 0, 0, 0
        x1, y1, z1 = 0, 0, self.L1

        # Primer segmento brazo
        x2 = x1 + self.L2 * np.cos(angulo_brazo_radianes) * np.cos(angulo_base_radianes)
        y2 = y1 + self.L2 * np.cos(angulo_brazo_radianes) * np.sin(angulo_base_radianes)
        z2 = z1 + self.L2 * np.sin(angulo_brazo_radianes)

        # Segundo segmento codo
        x3 = x2 + self.L3 * np.cos(
            angulo_brazo_radianes + angulo_codo_radianes
        ) * np.cos(angulo_base_radianes)
        y3 = y2 + self.L3 * np.cos(
            angulo_brazo_radianes + angulo_codo_radianes
        ) * np.sin(angulo_base_radianes)
        z3 = z2 + self.L3 * np.sin(angulo_brazo_radianes + angulo_codo_radianes)

        return (x0, x1, x2, x3), (y0, y1, y2, y3), (z0, z1, z2, z3)

    # ------------------------------
    #   Crea el grafico
    # ------------------------------
    def crear_grafico(self):
        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection="3d")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_diagrama)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.actualizar_grafico()

    # ------------------------------
    #   Actualiza el grafico
    # ------------------------------

    def actualizar_grafico(self, *args):
        ang_base = self.slider_vals["base"].get()
        ang_brazo = self.slider_vals["brazo"].get()
        ang_codo = self.slider_vals["codo"].get()
        ang_pinza = self.slider_vals["pinza"].get()

        xs, ys, zs = self.cinematicas_3d(ang_base, ang_brazo, ang_codo)

        self.ax.clear()
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_zlim(0, 15)
        self.ax.set_title("Brazo Robótico 3D")

        # Segmentos
        self.ax.plot(xs[0:2], ys[0:2], zs[0:2], color="red", linewidth=3)
        self.ax.plot(xs[1:3], ys[1:3], zs[1:3], color="green", linewidth=3)
        self.ax.plot(xs[2:4], ys[2:4], zs[2:4], color="orange", lw=3, marker="o")

        # PINZA
        x_end, y_end, z_end = xs[-1], ys[-1], zs[-1]
        l_pinza = 1.0
        thp = np.radians(ang_pinza)

        x_p1 = x_end + l_pinza * np.sin(thp / 2)
        x_p2 = x_end - l_pinza * np.sin(thp / 2)

        self.ax.plot([x_end, x_p1], [y_end, y_end], [z_end, z_end], color="blue", linewidth=2)
        self.ax.plot([x_end, x_p2], [y_end, y_end], [z_end, z_end], color="blue", linewidth=2)

        self.canvas.draw()

    # ------------------------------
    def volver_al_menu(self):
        if self.volver_callback:
            self.volver_callback()
        self.destroy()

    def cerrar_completamente(self):
        if hasattr(self, "after_id") and self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass

        try:
            plt.close(self.fig)
        except Exception:
            pass

        if self.volver_callback:
            self.volver_callback()

        self.destroy()


# ------------------------------
# Para prueba local
# ------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    root.after(100, lambda: root.state("zoomed"))

    def mostrar():
        root.deiconify()

    app = ModoManual(root, volver_callback=mostrar)
    root.withdraw()
    root.mainloop()
