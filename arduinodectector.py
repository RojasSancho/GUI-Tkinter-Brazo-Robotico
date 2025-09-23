import serial.tools.list_ports


"""Para depurar, indica que dispositivos estan conectados en los puertos """
#print("Puertos siendo utilizados:")
#puertos = serial.tools.list_ports.comports()
#for puerto in puertos:
#    print(puerto)


class ArduinoDetector:
    #Clase para detectar si un Arduino está conectado.

    def __init__(self):
        self.puerto = None

    def detectar(self):
        """Busca un puerto serie donde haya un Arduino conectado."""
        puertos = serial.tools.list_ports.comports()

        for puerto in puertos:
            if "USB" in puerto.description or "Dispositivo serie" in puerto.description:
                self.puerto = puerto.device
                print("Arduino detectado en", self.puerto)
                return True

        self.puerto = None
        return False

    def obtener_puerto(self):
        #Devuelve el puerto del Arduino si esta conectado
        return self.puerto
    

