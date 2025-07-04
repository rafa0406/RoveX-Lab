# config.py

# --- fichier de description du rover ---
ROVER_URDF_PATH = 'my-robot/robot.urdf'

# --- Parametres de Generation du Monde ---
TERRAIN_SIZE = 50
TERRAIN_SEGMENTS = 10  # Vous pouvez laisser cette valeur haute maintenant
VERTICES_PER_FRAME = 2000 # Nombre de points calcules par image. Augmentez pour aller plus vite, baissez si l'UI ralentit.
NUM_OBSTACLES = 0
OBSTACLE_SAFE_ZONE = 20

# --- Parametres de la Simulation Physique ---
ROVER_SPEED = 7
ROVER_ROTATION_SPEED = 75
GRAVITY_STRENGTH = 9.2
TERRAIN_FOLLOW_SMOOTHNESS = 10
TERRAIN_ADAPTATION_SMOOTHNESS = 5

# --- Parametres de la Camera ---
CAMERA_DISTANCE = 100
CAMERA_HEIGHT = 7
CAMERA_FOLLOW_SMOOTHNESS = 2

# --- Parametres du Rover ---
RIDE_HEIGHT = 0.7

# --- Parametres des Logs ---
MAX_LOG_MESSAGES = 50 # Augmente pour voir plus de logs