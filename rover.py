# rover.py
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time, destroy
from ursina.shaders import lit_with_shadows_shader
import config
import json

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, assembly_path, parts_mapping_path, **kwargs):
        super().__init__(**kwargs)
        
        self.ground = ground
        self.obstacles = obstacles
        self.logger = logger
        
        self.instances = {}
        self.wheels = []
        self.steering_joints = []
        self.body = None

        self.rotation_y = -90

        self._build_from_assembly(assembly_path, parts_mapping_path)
        
    def _build_from_assembly(self, assembly_path, parts_mapping_path):
        self.logger.log("--- DEBUT DE LA CONSTRUCTION DU ROVER ---", "info")
        
        # 1. Charger le dictionnaire de pièces
        self.logger.log(f"Lecture du mapping des pièces depuis '{parts_mapping_path}'...", "debug")
        try:
            with open(parts_mapping_path, 'r') as f:
                parts_map_data = json.load(f)
            parts_map = {item['id']: item for item in parts_map_data['parts_mapping']}
            self.logger.log(f"{len(parts_map)} mappings de pièces chargés.", "success")
        except Exception as e:
            self.logger.log(f"ERREUR CRITIQUE: Impossible de lire le fichier de mapping '{parts_mapping_path}'. Erreur: {e}", "error")
            return

        # 2. Charger et parser le fichier d'assemblage GLTF
        self.logger.log(f"Lecture de l'assemblage GLTF depuis '{assembly_path}'...", "debug")
        try:
            with open(assembly_path, 'r') as f:
                gltf_data = json.load(f)
            self.logger.log("Fichier d'assemblage GLTF chargé et parsé.", "success")
        except Exception as e:
            self.logger.log(f"ERREUR CRITIQUE: Impossible de lire le fichier d'assemblage '{assembly_path}'. Erreur: {e}", "error")
            return
        
        nodes_data = gltf_data.get('nodes', [])
        scenes_data = gltf_data.get('scenes', [])
        if not scenes_data:
            self.logger.log("ERREUR CRITIQUE: Aucune scène trouvée dans le fichier GLTF.", "error")
            return
        root_node_index = scenes_data[0]['nodes'][0]
        
        self.logger.log(f"Noeud racine trouvé à l'index: {root_node_index}", "debug")
        
        # 3. Fonction récursive pour construire la hiérarchie
        def build_node(node_index, parent_entity=None):
            if node_index >= len(nodes_data):
                self.logger.log(f"ERREUR: Index de noeud '{node_index}' hors des limites.", "error")
                return None

            node_info = nodes_data[node_index]
            node_name = node_info.get('name', f'UnnamedNode_{node_index}')
            self.logger.log(f"Traitement du noeud {node_index}: '{node_name}'", "debug")
            
            part_info = parts_map.get(node_name)
            if not part_info:
                self.logger.log(f"Alerte: Pièce '{node_name}' ignorée (pas de mapping dans le JSON).", "debug")
                # On traite quand même les enfants de ce noeud
                if 'children' in node_info:
                    for child_index in node_info['children']:
                        build_node(child_index, parent_entity)
                return None

            # Créer l'entité
            entity = Entity(
                name=node_name,
                model=part_info.get('model'),
                scale=part_info.get('scale', 1),
                shader=lit_with_shadows_shader,
                cast_shadows=True
            )
            self.logger.log(f"  -> Entité '{node_name}' créée.", "info")

            if 'translation' in node_info:
                entity.position = Vec3(*node_info['translation'])
                self.logger.log(f"  -> Position appliquée: {entity.position}", "debug")
            if 'rotation' in node_info:
                q = node_info['rotation']
                entity.quaternion = Quat(q[3], q[0], q[1], q[2])
                self.logger.log(f"  -> Rotation appliquée: {entity.quaternion}", "debug")

            self.instances[node_name] = entity
            
            if parent_entity:
                entity.parent = parent_entity
                self.logger.log(f"  -> Parenté établie avec '{parent_entity.name}'.", "info")

            if part_info.get('type') == 'body': self.body = entity
            if part_info.get('type') == 'wheel': self.wheels.append(entity)
            
            if 'children' in node_info:
                self.logger.log(f"  -> Recherche d'enfants pour '{node_name}'...", "debug")
                for child_index in node_info['children']:
                    build_node(child_index, parent_entity=entity)
            
            return entity

        # Démarrer la construction
        build_node(root_node_index)

        if self.body:
            self.body.collider = 'box'
            self.body.parent = self
            self.logger.log("Le corps du rover a été défini et parenté à l'entité principale.", "success")
        else:
            self.logger.log("ERREUR CRITIQUE: Aucun corps ('body') n'a été assemblé pour le rover.", "error")

        self.logger.log(f"--- FIN DE LA CONSTRUCTION. {len(self.instances)} instances créées. ---", "info")


    def update(self):
        if not self.body: return

        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        self.rotation_y += rotation_input * config.ROVER_ROTATION_SPEED * time.dt
        
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        
        if move_direction != 0:
            move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
            self.position += move_vec
            if self.body.intersects(ignore=list(self.instances.values())).hit:
                 self.position -= move_vec
                 self.logger.log("Alerte: Collision!", "error")

        ray = raycast(self.world_position + self.up*2, self.down, ignore=list(self.instances.values()), distance=10)
        
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