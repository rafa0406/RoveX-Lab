# environment.py
from ursina import Entity, Mesh, color, Vec3, raycast, invoke
# --- DEBUT DE LA CORRECTION : Importer le shader ---
from ursina.shaders import lit_with_shadows_shader
# --- FIN DE LA CORRECTION ---
from perlin_noise import PerlinNoise
import random
import config

class TerrainGenerator(Entity):
    # ... (le debut de la classe est identique) ...
    def __init__(self, ground_entity, logger, progress_bar, on_complete, **kwargs):
        super().__init__(**kwargs)
        self.ground_entity = ground_entity; self.logger = logger
        self.progress_bar = progress_bar; self.on_complete = on_complete
        self.logger.log("Demarrage de la generation progressive du terrain...", "debug")
        self.noise = PerlinNoise(octaves=4, seed=random.randint(1, 1000))
        self.terrain_mesh = Mesh(vertices=[], triangles=[], normals=[])
        self.total_vertices = (config.TERRAIN_SEGMENTS + 1) * (config.TERRAIN_SEGMENTS + 1)
        self.current_vertex = 0; self.last_logged_progress = -1

    def update(self):
        if self.current_vertex >= self.total_vertices: return
        limit = min(self.current_vertex + config.VERTICES_PER_FRAME, self.total_vertices)
        for i in range(self.current_vertex, limit):
            z_idx = i // (config.TERRAIN_SEGMENTS + 1)
            x_idx = i % (config.TERRAIN_SEGMENTS + 1)
            world_x = (x_idx - config.TERRAIN_SEGMENTS / 2) * (config.TERRAIN_SIZE / config.TERRAIN_SEGMENTS)
            world_z = (z_idx - config.TERRAIN_SEGMENTS / 2) * (config.TERRAIN_SIZE / config.TERRAIN_SEGMENTS)
            height, frequency, amplitude = 0, 2.5 / config.TERRAIN_SIZE, 12
            for j in range(4):
                height += self.noise([world_x * frequency, world_z * frequency]) * amplitude
                frequency *= 2.5; amplitude *= 0.4
            self.terrain_mesh.vertices.append(Vec3(world_x, height, world_z))
        self.current_vertex = limit
        progress = self.current_vertex / self.total_vertices
        self.progress_bar.set_progress(progress)
        progress_percent = int(progress * 100)
        if progress_percent // 10 > self.last_logged_progress // 10:
             self.logger.log(f"Generation du terrain : {progress_percent}%")
             self.last_logged_progress = progress_percent
        if self.current_vertex >= self.total_vertices:
            invoke(self.finish_generation, delay=0.01)
            self.enabled = False

    def finish_generation(self):
        self.logger.log("Finalisation... (Creation des triangles)", "debug")
        self.progress_bar.text.text = "Creation des triangles..."
        width = config.TERRAIN_SEGMENTS + 1
        for z in range(config.TERRAIN_SEGMENTS):
            for x in range(config.TERRAIN_SEGMENTS):
                i = z * width + x
                self.terrain_mesh.triangles.extend((i, i + 1, i + width))
                self.terrain_mesh.triangles.extend((i + 1, i + width + 1, i + width))
        invoke(self.finish_normals_and_collider, delay=0.01)
        
    def finish_normals_and_collider(self):
        self.logger.log("Finalisation... (Calcul des normales)", "debug")
        self.progress_bar.text.text = "Calcul des normales..."
        invoke(self._generate_normals, delay=0.01)

    def _generate_normals(self):
        self.terrain_mesh.generate_normals()
        invoke(self._apply_model, delay=0.01)

    def _apply_model(self):
        self.logger.log("Finalisation... (Application du maillage)", "debug")
        self.progress_bar.text.text = "Finalisation..."
        self.ground_entity.model = self.terrain_mesh
        self.ground_entity.collider = 'mesh'
        self.ground_entity.color = color.hex('5a6a7a')
        self.ground_entity.receive_shadows = True
        
        # --- DEBUT DE LA CORRECTION : Forcer l'utilisation du bon shader ---
        self.ground_entity.shader = lit_with_shadows_shader
        # --- FIN DE LA CORRECTION ---
        
        self.logger.log("Terrain genere avec succes.", "success")
        if self.on_complete: self.on_complete()
        self.progress_bar.enabled = False

class EnvironmentController:
    # ... (le reste de la classe est identique) ...
    def __init__(self, logger):
        self.logger = logger
        self.obstacles = []
    def start_terrain_generation(self, ground_entity, progress_bar, on_complete):
        return TerrainGenerator(
            ground_entity=ground_entity, logger=self.logger,
            progress_bar=progress_bar, on_complete=on_complete)
    def place_obstacles(self, ground_entity):
        self.logger.log("Placement des obstacles...")
        while len(self.obstacles) < config.NUM_OBSTACLES:
            x = random.uniform(-config.TERRAIN_SIZE / 2, config.TERRAIN_SIZE / 2)
            z = random.uniform(-config.TERRAIN_SIZE / 2, config.TERRAIN_SIZE / 2)
            if Vec3(x, 0, z).length() < config.OBSTACLE_SAFE_ZONE: continue
            hit_info = raycast(origin=Vec3(x, 100, z), direction=Vec3(0, -1, 0), ignore=[], distance=200)
            if hit_info.hit and hit_info.entity == ground_entity:
                rock = Entity(
                    model='sphere', subdivisions=2, scale=random.uniform(1.2, 2.5),
                    color=color.hex('8c7b6a'), position=hit_info.world_point,
                    rotation=(random.uniform(0,360), random.uniform(0,360), random.uniform(0,360)),
                    collider='box', cast_shadows=True,
                    # Les rochers doivent aussi avoir le bon shader
                    shader=lit_with_shadows_shader)
                rock.y -= (random.uniform(0.2, 0.5) * rock.scale_y)
                self.obstacles.append(rock)
        self.logger.log(f"{len(self.obstacles)} rochers places.", "success")
        return self.obstacles