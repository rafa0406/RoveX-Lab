# rover.py (version révisée pour assemblage complet)
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time, destroy
from ursina.shaders import lit_with_shadows_shader
import config

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, assembly_path, **kwargs):
        # On charge l'ENTIER de l'assemblage GLTF
        super().__init__(
            model=assembly_path,
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            **kwargs
        )

        self.ground = ground
        self.obstacles = obstacles
        self.logger = logger

        # Dictionnaires pour stocker les références aux parties mobiles
        self.wheels = {}
        self.body = None

        # Appliquer un collider global pour la physique générale
        self.collider = 'box'
        
        # Lancer la recherche récursive des pièces importantes dans le modèle chargé
        self._find_parts_in_hierarchy()
        
        # Appliquer la correction d'orientation globale
        self.rotation_y = 90
        
    def _find_parts_in_hierarchy(self):
        """
        Parcourt la hiérarchie du modèle chargé pour trouver, par leur nom, les entités 
        qui nous intéressent (roues, châssis) et les stocker.
        """
        self.logger.log("Recherche des pièces dans la hiérarchie du modèle...", "info")

        # Le nom des pièces doit correspondre à ce qui est défini dans Onshape
        WHEEL_NAMES = [
            'weel_left_front', 'weel_right_front',
            'weel_left_midle', 'weel_right_midle',
            'weel_left_rear', 'weel_right_rear'
        ]
        BODY_NAME = 'chassis'

        # `self.children` contient la hiérarchie directe du GLTF
        for entity in self.walk(): # .walk() parcourt tous les descendants
            # On cherche une correspondance partielle du nom
            if BODY_NAME in entity.name:
                self.body = entity
                self.logger.log(f"-> Corps principal trouvé: '{entity.name}'", "success")
                entity.shader = lit_with_shadows_shader # Assurer que le shader est appliqué

            for wheel_name in WHEEL_NAMES:
                if wheel_name in entity.name:
                    # La clé sera le nom complet trouvé, ex: 'ROVER_V1 - weel_left_front'
                    self.wheels[entity.name] = entity
                    self.logger.log(f"-> Roue trouvée: '{entity.name}'", "success")
                    entity.shader = lit_with_shadows_shader

        if not self.body:
            self.logger.log("ERREUR: Le corps du rover n'a pas été trouvé. Vérifiez le nom 'chassis' dans votre modèle.", "error")
        if not self.wheels:
            self.logger.log("AVERTISSEMENT: Aucune roue n'a été trouvée. Vérifiez les noms des roues.", "error")

    def update(self):
        if not self.body:
            return

        # La physique et les contrôles s'appliquent à l'entité parente 'self'
        ray = raycast(self.world_position + self.up*2, self.down, ignore=[self], distance=10)
        
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
        
        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        self.rotation_y -= rotation_input * config.ROVER_ROTATION_SPEED * time.dt
        
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        
        if move_direction != 0:
            if not self.intersects(ignore=[self, self.ground]).hit:
                move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
                self.position += move_vec
            else:
                self.logger.log("Alerte: Collision!", "error")
        
        # Rotation des roues trouvées dans la hiérarchie
        if move_direction != 0:
            for wheel_entity in self.wheels.values():
                # L'axe de rotation dépend de l'orientation de la pièce dans l'assemblage
                wheel_entity.rotation_x -= move_direction * 200 * time.dt