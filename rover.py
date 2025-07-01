# rover.py
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time, destroy
from ursina.shaders import lit_with_shadows_shader
import config
import json

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, assembly_path, parts_mapping_path, **kwargs):
        # On initialise une entité VIDE. Le modèle sera construit pièce par pièce.
        super().__init__(**kwargs)
        
        self.ground = ground
        self.obstacles = obstacles
        self.logger = logger
        
        self.instances = {}
        self.wheels = []
        self.body = None # Sera défini lors de la configuration

        # On applique le collider à l'entité principale du Rover pour gérer la physique globale.
        self.collider = 'box'
        
        # --- DEBUT DU TEST D'ORIENTATION ---
        # On ajoute une "poutre" rouge vif qui pointe dans la direction self.forward
        # pour vérifier visuellement l'orientation du rover.
        Entity(
            parent=self,
            model='cube',
            color=color.red,
            scale=(0.05, 0.05, 4), # Longue et fine pour bien voir la direction
            position=(0, 0.5, 2)  # On la décale un peu pour qu'elle soit bien visible
        )
        self.logger.log("Test d'orientation : Une poutre rouge indique la direction 'AVANT' du code.", "debug")
        # --- FIN DU TEST D'ORIENTATION ---

        self._setup_parts_from_json(parts_mapping_path)
        
    def _setup_parts_from_json(self, parts_mapping_path):
        """
        Cette nouvelle fonction lit le JSON et charge chaque pièce comme une entité distincte,
        en la parentant à l'entité principale du Rover.
        """
        self.logger.log("--- DEBUT DE LA CONFIGURATION DES PIECES (Nouvelle Methode) ---", "info")
        
        try:
            with open(parts_mapping_path, 'r') as f:
                parts_map_data = json.load(f)
            parts_mapping = parts_map_data['parts_mapping']
            self.logger.log(f"Mapping pour {len(parts_mapping)} pièces chargé.", "success")
        except Exception as e:
            self.logger.log(f"ERREUR CRITIQUE: Impossible de lire le fichier de mapping '{parts_mapping_path}'. Erreur: {e}", "error")
            return

        for part_info in parts_mapping:
            part_id = part_info.get('id')
            model_path = part_info.get('model')
            part_type = part_info.get('type')

            if not model_path:
                self.logger.log(f"Aucun modèle trouvé pour la pièce '{part_id}' dans le JSON.", "error")
                continue

            part_entity = Entity(
                parent=self,  # On parente la pièce à l'entité Rover
                model=model_path,
                shader=lit_with_shadows_shader,
                cast_shadows=True
            )

            # --- PATCH D'ORIENTATION ---
            # On applique une rotation de -90 degrés sur l'axe Y pour aligner
            # l'avant du modèle (+X) avec l'avant du code (+Z).
            part_entity.rotation_y = 90
            # -------------------------
            
            self.instances[part_id] = part_entity

            if part_type == 'body':
                self.body = part_entity # On garde une référence, mais le collider est sur le parent
                self.logger.log(f"-> Corps principal '{part_id}' identifié.", "debug")

            if part_type == 'wheel':
                self.wheels.append(part_entity)
                self.logger.log(f"-> Roue '{part_id}' identifiée.", "debug")

        if not self.body:
            self.logger.log("ERREUR CRITIQUE: Le corps ('body') n'a pas été configuré. La physique sera désactivée.", "error")
        else:
            self.logger.log("Corps du rover trouvé. La physique et les contrôles sont activés.", "success")
        
        self.logger.log("--- FIN DE LA CONFIGURATION DES PIECES ---", "info")


    def update(self):
        # Cette condition est maintenant la clé. Si le corps est trouvé, tout s'exécute.
        if not self.body: 
            return

        # --- Physique : Gravité et adaptation au terrain ---
        ray = raycast(self.world_position + self.up*2, self.down, ignore=[self, *self.instances.values()], distance=10)
        
        if ray.hit and ray.entity == self.ground:
            # Atterrissage en douceur et suivi du terrain
            target_y = ray.world_point.y + config.RIDE_HEIGHT
            self.y = lerp(self.y, target_y, time.dt * config.TERRAIN_FOLLOW_SMOOTHNESS)
            
            # Adaptation de l'inclinaison du rover à la pente du terrain
            calculator = Entity(position=self.position, add_to_scene_entities=False)
            calculator.look_at(self.world_position + self.forward, up=ray.world_normal)
            target_quat = calculator.quaternion
            destroy(calculator)
            
            self.quaternion = slerp(self.quaternion, target_quat, time.dt * config.TERRAIN_ADAPTATION_SMOOTHNESS)
        else:
            # Si le rover est en l'air, la gravité s'applique
            self.y -= config.GRAVITY_STRENGTH * time.dt
            
        # --- Contrôles ---
        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        # Note : j'ai inversé le signe pour que la flèche droite tourne à droite.
        self.rotation_y -= rotation_input * config.ROVER_ROTATION_SPEED * time.dt
        
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        
        if move_direction != 0:
            move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
            # La détection de collision se fait sur l'entité principale qui a le collider
            if self.intersects(ignore=[self, self.ground, *self.instances.values()]).hit:
                 self.logger.log("Alerte: Collision!", "error")
            else:
                 self.position += move_vec

        # --- Effet visuel : rotation des roues ---
        if move_direction != 0:
            for wheel in self.wheels:
                # Note: 'rotation_z' est correct si vos roues sont modélisées "à plat".
                # Sinon, vous pourriez avoir besoin de 'rotation_x' ou 'rotation_y'.
                wheel.rotation_x -= move_direction * 200 * time.dt