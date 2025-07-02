# rover.py
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time, destroy, load_model, invoke
from ursina.shaders import lit_with_shadows_shader
from urdf_parser_py.urdf import URDF
import numpy as np
import config
import os

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, urdf_path, **kwargs):
        # L'entité Rover elle-même est maintenant un conteneur vide.
        super().__init__(**kwargs)
        
        self.ground = ground
        self.obstacles = obstacles
        self.logger = logger
        self.urdf_path = urdf_path
        
        self.links = {}  # Dictionnaire pour stocker les entités de chaque "link"
        self.joints = {} # Dictionnaire pour stocker les infos des "joints"
        
        self.logger.log(f"Chargement du fichier URDF: {urdf_path}", "info")
        
        # Le chargement est différé pour s'assurer que l'environnement est prêt
        invoke(self.build_from_urdf, delay=0.01)

    def build_from_urdf(self):
        try:
            # 1. Parser le fichier URDF
            robot = URDF.from_xml_file(self.urdf_path)
            urdf_dir = os.path.dirname(self.urdf_path)

            # 2. Créer une entité Ursina pour chaque "link"
            for link in robot.links:
                # Vérifier si le link a une géométrie visuelle
                if not (link.visual and link.visual.geometry and link.visual.geometry.filename):
                    continue
                
                raw_mesh_path = link.visual.geometry.filename
                
                # --- CORRECTION ---
                # On supprime le préfixe 'package://' si celui-ci est présent dans le chemin.
                if raw_mesh_path.startswith('package://'):
                    clean_mesh_path = raw_mesh_path.replace('package://', '', 1)
                else:
                    clean_mesh_path = raw_mesh_path
                
                # On construit le chemin final relatif au dossier du fichier URDF.
                mesh_path = os.path.join(urdf_dir, clean_mesh_path).replace('\\', '/')
                
                if not os.path.exists(mesh_path):
                    self.logger.log(f"Erreur: Fichier mesh introuvable: {mesh_path}", "error")
                    continue
                
                # Création de l'entité pour ce link
                link_entity = Entity(
                    name=link.name,
                    model=load_model(mesh_path, use_deepcopy=True),
                    shader=lit_with_shadows_shader,
                    color=color.light_gray,
                    cast_shadows=True
                )
                self.links[link.name] = link_entity
                self.logger.log(f"-> Link '{link.name}' créé.", "success")
            
            # ... (Le reste de la fonction pour assembler les joints est inchangé) ...
            
        except Exception as e:
            self.logger.log(f"ERREUR CRITIQUE lors du parsing URDF: {e}", "error")

    def update(self):
        # La logique de physique doit être adaptée pour gérer les suspensions.
        # Pour l'instant, on applique une physique simplifiée au corps principal.
        
        root_link_name = "base_link" # Nom standard pour le châssis, à adapter si besoin
        if not self.links.get(root_link_name):
            return # Ne rien faire si le rover n'est pas encore construit

        # --- Physique simplifiée (similaire à avant) ---
        ray = raycast(self.world_position + self.up*2, self.down, ignore=[self, *self.links.values()], distance=10)
        
        if ray.hit and ray.entity == self.ground:
            target_y = ray.world_point.y + config.RIDE_HEIGHT
            self.y = lerp(self.y, target_y, time.dt * config.TERRAIN_FOLLOW_SMOOTHNESS)
            
            calculator = Entity(position=self.position, add_to_scene_entities=False)
            calculator.look_at(self.world_position + self.forward, up=ray.world_normal)
            target_quat = calculator.quaternion
            destroy(calculator)
            
            self.quaternion = slerp(self.quaternion, target_quat, time.dt * config.TERRAIN_ADAPTATION_SMOOTHNESS)
        else: 
            self.y -= config.GRAVITY_STRENGTH * time.dt
        
        # --- Contrôles (inchangés) ---
        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        self.rotation_y -= rotation_input * config.ROVER_ROTATION_SPEED * time.dt
        
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        
        if move_direction != 0:
            move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
            # On vérifie la collision du châssis
            if not self.links[root_link_name].intersects(ignore=[self, *self.links.values()]).hit:
                self.position += move_vec
            else:
                self.logger.log("Alerte: Collision!", "error")