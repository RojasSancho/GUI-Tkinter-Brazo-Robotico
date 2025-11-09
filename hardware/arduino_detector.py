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
                self.puerto = puerto.device
                print("Arduino detectado en", self.puerto)
                return True

        self.puerto = None
        print("No se ha detectado ningun Arduino conectado.")
        return False

    def obtener_puerto(self):
        # Devuelve el puerto del Arduino si esta conectado
        return self.puerto

    def conectar(self, baudrate=9600, timeout=1):
        """Intenta abrir la conexión con el Arduino en el puerto detectado."""
        if not self.puerto:
            print("No es posible conectar, Arduino no detectado")
            return False

        try:
            self.conexion = serial.Serial(self.puerto, baudrate, timeout=timeout)
            time.sleep(2)
            print(f"Conectado al Arduino en {self.puerto}")
            return True
        except serial.SerialException as e:
            print(f"Error al conectar con {self.puerto}: {e}")
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
