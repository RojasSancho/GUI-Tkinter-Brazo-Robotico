import serial
import serial.tools.list_ports
import time


"""Para depurar, indica que dispositivos estan conectados en los puertos """
# print("Puertos siendo utilizados:")
# puertos = serial.tools.list_ports.comports()
# for puerto in puertos:
#    print(puerto)


class ArduinoDetector:
    """
    Clase para detectar y comunicarse con un Arduino conectado por USB.
    """

    def __init__(self):
        self.puerto = None
        self.conexion = None
        self.estado_arduino = "desconectado"  # lleva control del estado

    def detectar(self):
        """Busca un puerto serie donde haya un Arduino conectado."""
        puertos = serial.tools.list_ports.comports()

        for puerto in puertos:
            descripcion = puerto.description.lower()
            if (
                "arduino" in descripcion
                or "usb serial" in descripcion
                or "dispositivo serie" in descripcion
            ):
                if self.puerto != puerto.device:
                    self.puerto = puerto.device
                    print("Arduino detectado en", self.puerto)
                return True

        # Si antes había uno conectado y ya no

        if self.estado_arduino != "desconectado":
            print("Arduino desconectado.")
            self.estado_arduino = "desconectado"
            self.puerto = None
        return False

    def obtener_puerto(self):
        # Devuelve el puerto del Arduino si esta conectado
        return self.puerto

    def conectar(self, baudrate=9600, timeout=1):
        """Intenta abrir la conexión con el Arduino en el puerto detectado."""
        if not self.puerto:
            return False

        # Cerrar conexión previa si sigue abierta
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            time.sleep(0.5)

        try:
            self.conexion = serial.Serial(self.puerto, baudrate, timeout=timeout)
            time.sleep(2)
            self.estado_arduino = "conectado"
            print(f"Conectado al Arduino en {self.puerto}")
            print("Arduino conectado correctamente.")
            return True
        except (serial.SerialException, FileNotFoundError):
            self.estado_arduino = "desconectado"
            return False

    def enviar_rutina(self, rutina, repeticiones):
        """Envía una rutina y el número de repeticiones al Arduino."""
        if not self.conexion or not self.conexion.is_open:
            print("No existe conexion activa con un Arduino")
            return False

        try:
            mensaje = f"{rutina},{repeticiones}\n"
            self.conexion.write(mensaje.encode("utf-8"))  # Usar UTF-8
            print(f"Mensaje enviado al Arduino: {mensaje.strip()}")
            return True
        except serial.SerialException as e:
            print(f"Error al enviar datos: {e}")
            return False

    def cerrar(self):
        """Cierra la conexion serie."""
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            print("Conexion serie con Arduino cerrada.")
        self.estado_arduino = "desconectado"

    def revisar_conexion(self):
        """Verifica si el Arduino sigue conectado y trata de reconectar si es necesario."""
        puertos_actuales = [p.device for p in serial.tools.list_ports.comports()]

        # Si el puerto desapareció, desconexión
        if self.puerto and self.puerto not in puertos_actuales:
            if self.estado_arduino != "desconectado":
                print("Arduino desconectado.")
                self.cerrar()
            self.puerto = None
            self.conexion = None
            self.estado_arduino = "desconectado"
            return False

        # Si no hay conexión, intentar reconectar
        if (not self.conexion or not self.conexion.is_open) and self.detectar():
            if self.estado_arduino != "conectado":
                print("Arduino detectado, intentando reconectar...")
                if self.conectar():
                    self.estado_arduino = "conectado"
                    return True
        elif not self.detectar():
            if self.estado_arduino != "desconectado":
                print("Arduino desconectado.")
                self.estado_arduino = "desconectado"

        return self.esta_conectado()

    def esta_conectado(self):
        """Devuelve True si la conexión serie con el Arduino está activa."""
        return self.conexion is not None and self.conexion.is_open
