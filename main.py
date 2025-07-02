# main.py
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from logger import LogWindow
from environment import EnvironmentController
from rover import Rover
import config

class ProgressBar(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui, model='quad', scale=(0.8, 0.04),
            position=(0, 0.05), color=color.dark_gray)
        self.bar = Entity(parent=self, model='quad', color=color.azure,
            origin=(-0.5, 0), position=(-0.5, 0), scale=(0, 1))
        self.text = Text(parent=self, text="Génération du Terrain...",
            origin=(0, -2.5), color=color.white)

    def set_progress(self, value):
        self.bar.scale_x = value
        if value < 1:
            self.text.text = f"Génération des vertices... {int(value * 100)}%"

if __name__ == '__main__':
    app = Ursina(title='RoverX Lab', size=(1280, 720), vsync=True, borderless=False)

    ground = None
    log_window = LogWindow()
    progress_bar = ProgressBar()
    log_window.log("Application initialisée.")
    env_controller = EnvironmentController(logger=log_window)

    def start_simulation():
        """
        Cette fonction est appelée après que le terrain est généré et prêt.
        """
        global rover
        log_window.log("Création des éléments de simulation...")

        obstacles = env_controller.place_obstacles(ground)

        safe_spawn_pos = (0, 25, 0)
        log_window.log(f"Création du rover à une altitude sûre : {safe_spawn_pos}", "debug")

        # On crée l'instance du rover. La classe Rover s'occupe du reste
        # en lisant le chemin URDF depuis config.py.
        rover = Rover(
            ground=ground,
            obstacles=obstacles,
            logger=log_window,
            position=safe_spawn_pos
        )

        log_window.log("Simulation prête. Déplacement : flèches.", "success")


    def on_generation_complete():
        log_window.log("Maillage du terrain terminé. Initialisation de la physique...")
        invoke(start_simulation, delay=0.1)

    # Initialisation de la génération du terrain
    ground = Entity()
    env_controller.start_terrain_generation(
        ground_entity=ground, progress_bar=progress_bar,
        on_complete=on_generation_complete)

    # Configuration de la scène
    window.color = color.black
    sun = DirectionalLight(y=50, z=50, x=50, shadows=True)
    ambient = AmbientLight(color=color.rgba(100, 100, 100, 0.1))
    
    # Caméra libre pour le débogage
    EditorCamera(rotation_speed=200, pan_speed=(50, 50), zoom_speed=1.5)

    app.run()