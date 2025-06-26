RoverX Lab
Statut du projet : Prototype fonctionnel (v1.2)

1. À propos du Projet
RoverX Lab est un simulateur 3D accessible via le web, conçu comme un banc d'essai (Testbed) pour le développement et la validation de rovers d'exploration planétaire. Le projet a pour but de fournir un environnement virtuel réaliste et difficile, permettant aux ingénieurs, développeurs et chercheurs de tester la conception mécanique et les algorithmes de navigation de leurs engins avant leur déploiement sur le terrain.

L'objectif n'est pas de créer un jeu, mais une plateforme de simulation professionnelle qui sert de "bac à sable" (sandbox) pour l'ingénierie robotique.

2. Objectif
La mission principale de RoverX Lab est de fournir une base robuste et flexible pour :

Simuler des environnements complexes : Génération de terrains procéduraux avec des reliefs variés (collines, pentes) et des obstacles (rochers).

Simuler la physique du rover : Interaction réaliste avec le sol, gestion des pentes et détection de collisions.

Offrir une interface de test : À terme, le projet fournira une API (Interface de Programmation Applicative) claire pour permettre à des tiers d'intégrer leurs propres designs de rovers et, surtout, leurs propres algorithmes de navigation autonomes.

3. Fonctionnalités Actuelles (v1.2)
Moteur de rendu 3D web : Visualisation en temps réel directement dans le navigateur.

Génération de terrain procédurale : Chaque session de simulation se déroule sur un terrain unique généré aléatoirement.

Physique du rover :

Le rover s'adapte aux pentes du terrain (tangage et roulis).

La caméra suit intelligemment le rover pour une meilleure visibilité.

Détection de collision simple avec les obstacles.

Placement d'obstacles réaliste : Les rochers sont générés aléatoirement sur la carte, en contact avec le sol et partiellement enfouis pour plus de réalisme.

Zone de départ sécurisée : Le rover apparaît toujours dans une clairière dégagée pour éviter les blocages au démarrage.

Contrôle manuel : Le rover peut être piloté manuellement avec les touches directionnelles du clavier ou des boutons tactiles, servant d'outil de test de base.

Fenêtre de log : Une interface de journalisation en temps réel affiche les étapes clés du chargement et de la simulation.

4. Comment Utiliser la Simulation
Lancement : Ouvrez le fichier index.html (ou l'URL de l'application) dans un navigateur web moderne.

Génération : Patientez quelques instants pendant que le terrain est généré. Vous pouvez suivre la progression dans la fenêtre de log sur la gauche.

Contrôle manuel:

Avancer : Touche ↑ ou bouton ▲.

Reculer : Touche ↓ ou bouton ▼.

Tourner à gauche : Touche ← ou bouton ◀.

Tourner à droite : Touche → ou bouton ▶.

Contrôle API:

Interface à définir.

5. Vision Future
La version actuelle est une base solide. Les prochaines grandes étapes de développement se concentreront sur la transformation de ce prototype en une véritable plateforme :

Développement de l'API Rover :

Créer une interface JavaScript simple pour permettre de définir un rover (nombre de roues, dimensions, capteurs).

Exposer des fonctions pour contrôler le rover par code (ex: rover.setMotorSpeed(wheel_index, speed)).

Développement de l'API Capteurs :

Simuler des capteurs virtuels (caméras, LiDAR, IMU) dont les données seront accessibles via l'API.

Permettre aux algorithmes de navigation externes de recevoir ces données pour prendre des décisions.

Amélioration de la physique :

Simuler des suspensions plus complexes (ex: Rocker-bogie).

Gérer le glissement et le patinage des roues en fonction du type de sol.

6. Stack Technique
Moteur 3D : Three.js

Langage : JavaScript (ES6 Modules)

Interface : HTML5 / CSS3 (avec Tailwind CSS)
