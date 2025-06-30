# rover.py
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time, destroy
from ursina.shaders import lit_with_shadows_shader
import config
import json

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, assembly_path, parts_mapping_path, **kwargs):
        # Initialiser l'entité Rover avec l'assemblage complet
        super().__init__(
            model=assembly_path,
            **kwargs
        )
        
        self.ground = ground
        self.obstacles = obstacles
        self.logger = logger
        
        self.instances = {}
        self.wheels = []
        self.steering_joints = []
        self.body = None

        self.rotation_y = -90 # Rotation initiale pour orienter le rover correctement

        self._setup_parts(parts_mapping_path)
        
    def _setup_parts(self, parts_mapping_path):
        self.logger.log("--- DEBUT DE LA CONFIGURATION DES PIECES ---", "info")
        
        try:
            with open(parts_mapping_path, 'r') as f:
                parts_map_data = json.load(f)
            parts_map = {item['id']: item for item in parts_map_data['parts_mapping']}
            self.logger.log(f"Mapping pour {len(parts_map)} pièces chargé.", "success")
        except Exception as e:
            self.logger.log(f"ERREUR CRITIQUE: Impossible de lire le fichier de mapping '{parts_mapping_path}'. Erreur: {e}", "error")
            return
            
        # --- CORRECTION : Utilisation d'une fonction récursive ---
        # Cette fonction va parcourir tous les descendants de l'entité principale
        def configure_recursively(entity):
            # Chercher une correspondance dans notre dictionnaire de pièces
            part_info = parts_map.get(entity.name)
            
            if part_info:
                self.logger.log(f"Configuration de la pièce : '{entity.name}'", "info")
                
                # Appliquer le modèle visuel, le shader, etc.
                entity.model = part_info.get('model')
                entity.shader = lit_with_shadows_shader
                entity.cast_shadows = True
                self.instances[entity.name] = entity

                # Identifier les pièces importantes
                if part_info.get('type') == 'body':
                    self.body = entity
                    self.body.collider = 'box'
                    self.logger.log(f"-> Corps principal '{entity.name}' identifié.", "debug")

                if part_info.get('type') == 'wheel':
                    self.wheels.append(entity)
                    self.logger.log(f"-> Roue '{entity.name}' identifiée.", "debug")
            
            # Appel récursif pour les enfants de l'entité actuelle
            for child in entity.children:
                configure_recursively(child)

        # Démarrer la configuration récursive à partir de l'entité Rover elle-même
        configure_recursively(self)

        if not self.body:
            self.logger.log("ERREUR CRITIQUE: Aucun corps ('body') n'a été trouvé pour le rover.", "error")
        
        self.logger.log("--- FIN DE LA CONFIGURATION DES PIECES ---", "info")


    def update(self):
        # Cette condition est cruciale et fonctionnera maintenant correctement
        if not self.body: 
            return

        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        self.rotation_y += rotation_input * config.ROVER_ROTATION_SPEED * time.dt
        
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        
        if move_direction != 0:
            move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
            self.position += move_vec
            if self.body.intersects(ignore=[self, *self.instances.values()]).hit:
                 self.position -= move_vec
                 self.logger.log("Alerte: Collision!", "error")

        ray = raycast(self.world_position + self.up*2, self.down, ignore=[self, *self.instances.values()], distance=10)
        
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
        
        if move_direction != 0:
            for wheel in self.wheels:
                wheel.rotation_z -= move_direction * 200 * time.dt