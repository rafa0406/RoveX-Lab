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
        self.text = Text(parent=self, text="Generation du Terrain...",
            origin=(0, -2.5), color=color.white)
    def set_progress(self, value):
        self.bar.scale_x = value
        if value < 1:
            self.text.text = f"Generation des vertices... {int(value * 100)}%"

if __name__ == '__main__':
    app = Ursina(title='RoverX Lab', size=(1280, 720), vsync=True, borderless=False)

    ground = None; rover = None
    log_window = LogWindow()
    progress_bar = ProgressBar()
    log_window.log("Application initialisee.")
    env_controller = EnvironmentController(logger=log_window)

    def start_simulation():
        global rover
        log_window.log("Creation des elements de simulation...")
        
        obstacles = env_controller.place_obstacles(ground)
        
        safe_spawn_pos = (0, 25, 0)
        log_window.log(f"Creation du rover a une altitude sure: {safe_spawn_pos}", "debug")
        
        # --- MISE A JOUR ---
        # Le chemin pointe maintenant vers le nouveau fichier d'assemblage
        rover = Rover(
            ground=ground, 
            obstacles=obstacles, 
            logger=log_window, 
            position=safe_spawn_pos,
            assembly_path='assets/models/ROVER_V1/Rover_v1_Assembly.gltf',
            parts_mapping_path='rover_model_V1.json'
        )
            
        log_window.log("Simulation prete. Deplacement : fleches.", "success")


    def on_generation_complete():
        log_window.log("Maillage du terrain termine. Initialisation de la physique...")
        invoke(start_simulation, delay=0.1)

    ground = Entity()
    env_controller.start_terrain_generation(
        ground_entity=ground, progress_bar=progress_bar,
        on_complete=on_generation_complete)

    window.color = color.black
    sun = DirectionalLight(color=Vec4(1, 0.9, 0.8, 1), y=50, z=50, x=50, shadows=True)
    ambient = AmbientLight(color=Vec4(0.15, 0.15, 0.15, 1))
    
    EditorCamera(rotation_speed=200, pan_speed=(50, 50), zoom_speed=1.5)
    
    sun.shadows = True

    app.run()