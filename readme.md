# Control de Brazo Robótico

Aplicación en Python para controlar un brazo robótico con dos modos: **Manual** y **Automático**. Permite ejecutar subrutinas preprogramadas y visualizar videos de las rutinas en la interfaz.

---

## Características

- **Modo Manual:** Control directo del brazo robótico.
- **Modo Automático:** Ejecución de subrutinas predefinidas.
- Interfaz gráfica moderna con **CustomTkinter**.
- Visualización de videos asociados a cada rutina.
- Indicador de conexión con Arduino.
- Cambio de tema claro/oscuro.

---

## Requisitos

- Python 3.10 o superior
- pip

### Dependencias

Se pueden instalar todas con:

```bash
pip install -r requirements.txt
```


pyinstaller --clean --onefile --noconsole ventana.py

## Requisitos previos:
Antes de ejecutar la aplicación, asegúrese de instalar la fuente Bebas Neue que se encuentra en la carpeta fonts/ de este proyecto.
Esto garantiza que todos los textos y widgets se muestren correctamente.
