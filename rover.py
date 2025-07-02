# rover.py
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time, destroy, scene
from ursina.shaders import lit_with_shadows_shader
from urdf_parser_py.urdf import URDF
import config
import os
import math

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, **kwargs):
        super().__init__(**kwargs)
        
        self.ground = ground
        self.obstacles = obstacles
        self.logger = logger
        
        # Dictionnaires pour stocker les entités et les informations des articulations
        self.links = {}
        self.joints = {}
        self.wheels = []
        self.root_link = None # Pièce principale du rover (châssis)
        
        self.logger.log("Initialisation du chargement depuis l'URDF...", "info")
        self._setup_from_urdf(config.ROVER_URDF_PATH)

    def _setup_from_urdf(self, urdf_path):
        try:
            robot = URDF.from_xml_file(urdf_path)
            self.logger.log(f"Robot '{robot.name}' chargé depuis l'URDF.", "success")
        except Exception as e:
            self.logger.log(f"ERREUR CRITIQUE: Impossible de lire le fichier URDF '{urdf_path}'. Erreur: {e}", "error")
            return

        base_path = os.path.dirname(urdf_path)
        self.root_link = self.links.get(robot.get_root())

        # Étape 1 : Créer toutes les entités "pivot" pour chaque pièce
        for link in robot.links:
            pivot = Entity(parent=self, name=link.name)
            self.links[link.name] = pivot
            
            # Charger le modèle 3D comme un enfant du pivot
            if link.visual and link.visual.geometry and hasattr(link.visual.geometry, 'filename'):
                mesh_filename = link.visual.geometry.filename
                if mesh_filename.startswith('package://'):
                    mesh_filename = mesh_filename.split('//', 1)[1]
                
                full_mesh_path = os.path.join(base_path, mesh_filename).replace("\\", "/")

                Entity(
                    parent=pivot,
                    model=full_mesh_path,
                    shader=lit_with_shadows_shader,
                    cast_shadows=True,
                    # Rotation pour aligner le modèle si nécessaire (dépend de l'export)
                    rotation_y=90 
                )
                self.logger.log(f"-> Lien '{link.name}' créé avec le modèle '{full_mesh_path}'", "debug")

        # Étape 2 : Connecter les pivots en fonction des articulations
        for joint in robot.joints:
            parent_link = self.links.get(joint.parent)
            child_link = self.links.get(joint.child)

            if parent_link and child_link:
                child_link.parent = parent_link

                if joint.origin:
                    child_link.position = Vec3(*joint.origin.xyz)
                    r, p, y = [math.degrees(angle) for angle in joint.origin.rpy]
                    child_link.rotation = Vec3(r, p, y)
                
                self.joints[joint.name] = {
                    'parent': parent_link, 
                    'child': child_link, 
                    'axis': Vec3(*joint.axis) if joint.axis else Vec3(0,0,1),
                    'type': joint.type
                }
                
                # Identifier les roues pour l'animation
                if 'wheel' in joint.name or 'roue' in joint.name:
                    self.wheels.append(self.joints[joint.name])
                    self.logger.log(f"-> Roue identifiée sur l'articulation '{joint.name}'", "debug")
        
        self.logger.log("Construction du rover depuis l'URDF terminée.", "success")
        
        # Le collider principal est placé sur l'entité racine du rover
        self.collider = 'box'

    def update(self):
        if not self.links:
            return # Ne rien faire si le chargement a échoué

        # --- Physique : Gravité et adaptation au terrain ---
        ray = raycast(self.world_position + self.up * 2, self.down, ignore=[self, *self.children], distance=10)
        
        if ray.hit and ray.entity == self.ground:
            target_y = ray.world_point.y + config.RIDE_HEIGHT
            self.y = lerp(self.y, target_y, time.dt * config.TERRAIN_FOLLOW_SMOOTHNESS)
            
            # Adaptation de l'inclinaison du rover à la pente
            target_quat = Quat()
            target_quat.look_at(self.forward, direction=ray.world_normal)
            self.quaternion = slerp(self.quaternion, target_quat, time.dt * config.TERRAIN_ADAPTATION_SMOOTHNESS)
        else:
            self.y -= config.GRAVITY_STRENGTH * time.dt
            
        # --- Contrôles ---
        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        self.rotation_y -= rotation_input * config.ROVER_ROTATION_SPEED * time.dt
        
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        
        if move_direction != 0:
            move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
            # La détection de collision se fait sur l'entité principale
            if not self.intersects(ignore=[self, self.ground, *self.children]).hit:
                 self.position += move_vec
            else:
                 self.logger.log("Alerte: Collision!", "error")

        # --- Animation des articulations (exemple avec les roues) ---
        if move_direction != 0:
            for wheel_joint in self.wheels:
                # On fait tourner le PIVOT de la roue autour de son axe
                rotation_axis = wheel_joint['axis']
                pivot_to_rotate = wheel_joint['child']
                pivot_to_rotate.rotate(rotation_axis * move_direction * -200 * time.dt)