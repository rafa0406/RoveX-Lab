# logger.py
from ursina import Text, camera, color
from collections import deque
import config

class LogWindow:
    def __init__(self):
        self.log_messages = deque(maxlen=config.MAX_LOG_MESSAGES)
        self.log_display = Text(
            origin=(-0.5, 0.5),
            position=(-0.98 * camera.aspect_ratio, 0.48),
            scale=(0.7, 0.7),
            text=""
        )
        self.log("Logger initialise.", "success")

    def _update_display(self):
        self.log_display.text = "\n".join(self.log_messages)

    def log(self, message, level='info'):
        color_map = {
            'info': color.cyan,
            'success': color.green,
            'error': color.red,
            'debug': color.yellow
        }
        
        # Utilise les balises de couleur d'Ursina
        formatted_message = f'<{color_map.get(level, color.white)}>{message}<default>'
        self.log_messages.append(formatted_message)
        self._update_display()