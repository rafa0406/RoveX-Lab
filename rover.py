# rover.py
from ursina import Entity, color, Vec3, Quat, lerp, slerp, raycast, held_keys, time
from ursina import Cylinder
from ursina.shaders import lit_with_shadows_shader
import config

class Rover(Entity):
    def __init__(self, ground, obstacles, logger, **kwargs):
        super().__init__(model=None, **kwargs)
        
        self.ground = ground; self.obstacles = obstacles; self.logger = logger
        
        self.body = Entity(
            parent=self, model='cube', scale=(1.5, 0.5, 2.5),
            color=color.light_gray, texture='white_cube',
            cast_shadows=True, collider='box',
            shader=lit_with_shadows_shader)

        wheel_model = Cylinder(direction=(0,0,1))
        wheel_scale = (0.55, 0.55, 0.15)
        
        self.wheels = [
            Entity(parent=self.body, model=wheel_model, color=color.dark_gray, scale=wheel_scale, position=(0.6, -0.1, 0.7), shader=lit_with_shadows_shader),
            Entity(parent=self.body, model=wheel_model, color=color.dark_gray, scale=wheel_scale, position=(-0.6, -0.1, 0.7), shader=lit_with_shadows_shader),
            Entity(parent=self.body, model=wheel_model, color=color.dark_gray, scale=wheel_scale, position=(0.6, -0.1, -0.7), shader=lit_with_shadows_shader),
            Entity(parent=self.body, model=wheel_model, color=color.dark_gray, scale=wheel_scale, position=(-0.6, -0.1, -0.7), shader=lit_with_shadows_shader),
        ]
        
    def update(self):
        # --- DEBUT DE LA CORRECTION DEFINITIVE ---
        # 1. Rotation du joueur en utilisant la syntaxe correcte du constructeur Quat(angle, axis)
        rotation_input = held_keys['left arrow'] - held_keys['right arrow']
        # On passe les arguments sans les nommer.
        self.rotation *= Quat(rotation_input * config.ROVER_ROTATION_SPEED * time.dt, self.up)

        # 2. Deplacement (avant/arriere)
        move_direction = held_keys['up arrow'] - held_keys['down arrow']
        is_moving = False
        if move_direction != 0:
            move_vec = self.forward * move_direction * config.ROVER_SPEED * time.dt
            self.position += move_vec
            hit_info = self.body.intersects(ignore=[self.ground, self.body, *self.wheels])
            if hit_info.hit and hit_info.entity in self.obstacles:
                 self.position -= move_vec; self.logger.log("Alerte: Collision!", "error")
            else: is_moving = True

        # 3. Adaptation au terrain (stable)
        ray = raycast(self.world_position + self.up*2, self.down, ignore=[self, self.body, *self.wheels], distance=10)
        
        if ray.hit and ray.entity == self.ground:
            target_y = ray.world_point.y + config.RIDE_HEIGHT
            self.y = lerp(self.y, target_y, time.dt * config.TERRAIN_FOLLOW_SMOOTHNESS)
            
            current_quat = self.world_rotation
            self.look_at(self.position + self.forward, up=ray.world_normal)
            target_quat = self.rotation
            self.rotation = current_quat
            self.rotation = slerp(current_quat, target_quat, time.dt * config.TERRAIN_ADAPTATION_SMOOTHNESS)
        else: 
            self.y -= config.GRAVITY_STRENGTH * time.dt
        
        # --- FIN DE LA CORRECTION DEFINITIVE ---

        if is_moving:
            for wheel in self.wheels:
                wheel.rotation_z += move_direction * 200 * time.dt