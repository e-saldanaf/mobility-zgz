import colorlog
import logging

def configurar_logs():
    # 1. Crear el manejador para la consola (StreamHandler)
    handler = colorlog.StreamHandler()

    # 2. Definir los colores para cada nivel de log
    # Puedes usar: black, red, green, yellow, blue, magenta, cyan, white
    # "log_color" aplica el color del nivel al mensaje
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    # 3. Asignar el formateador de colores al manejador
    handler.setFormatter(formatter)

    # 4. Configurar el logger raíz
    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)  # Cambia esto al nivel mínimo que quieras ver