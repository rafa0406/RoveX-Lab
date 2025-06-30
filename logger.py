# logger.py
from ursina import Text, camera, color
from collections import deque
import config

class LogWindow:
    def __init__(self):
        self.log_messages = deque(maxlen=config.MAX_LOG_MESSAGES)
        
        # --- CORRECTION ---
        # Ajout de `parent=camera.ui` pour que le texte s'affiche sur l'interface 2D
        self.log_display = Text(
            parent=camera.ui,
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
        
        formatted_message = f'<{color_map.get(level, color.white)}>{message}<default>'
        self.log_messages.append(formatted_message)
        self._update_display()