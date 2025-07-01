# RoverX Lab
**Statut du projet : En développement (Migration vers Python/Ursina avec support URDF)**

## 1. À propos du Projet
RoverX Lab est un simulateur 3D conçu comme un banc d'essai (*Testbed*) pour le développement et la validation de rovers d'exploration planétaire. Le projet a pour but de fournir un environnement virtuel réaliste, permettant aux ingénieurs, développeurs et chercheurs de tester la conception mécanique et les algorithmes de navigation de leurs engins dans un "bac à sable" (*sandbox*) d'ingénierie robotique.

L'objectif n'est pas de créer un jeu, mais une plateforme de simulation professionnelle.

## 2. Objectif
La mission principale de RoverX Lab est de fournir une base robuste et flexible pour :

* **Simuler des environnements complexes** : Génération de terrains procéduraux avec des reliefs et des obstacles variés.
* **Simuler la physique du rover** : Interaction réaliste avec le sol, gestion des pentes et détection de collisions.
* **Fournir une architecture standardisée** : Utilisation du format **URDF** pour décrire le robot, permettant de charger facilement des modèles provenant de logiciels de CAO.
* **Offrir une interface de test** : À terme, le projet fournira une API Python claire pour permettre l'intégration d'algorithmes de navigation autonomes.

## 3. Stack Technique
* **Moteur de Simulation** : [Ursina Engine](https://www.ursinaengine.org/)
* **Langage** : Python 3
* **Description du Robot** : URDF (Unified Robot Description Format)

## 4. Fonctionnalités Actuelles
* **Moteur 3D Python** : Simulation et visualisation en temps réel avec le moteur Ursina.
* **Génération de Terrain Procédurale** : Chaque session se déroule sur un terrain unique, généré de manière asynchrone pour ne pas bloquer l'interface.
* **Chargement de Modèles via URDF** : Le simulateur charge la structure complète du rover (pièces, articulations, points de pivot) depuis un fichier `.urdf`, assurant une représentation fidèle du modèle CAO.
* **Physique du Rover (en cours)** :
    * Le rover est soumis à la gravité et s'adapte à la hauteur du terrain.
    * La structure des suspensions (ex: Rocker-bogie) est correctement assemblée en respectant les liaisons pivots.
* **Contrôles Manuels** : Le rover peut être piloté au clavier pour les tests de base.

## 5. Comment Lancer la Simulation

1.  **Prérequis** : Assurez-vous d'avoir Python 3 installé sur votre système.

2.  **Cloner le dépôt** (si ce n'est pas déjà fait) :
    ```bash
    git clone [URL_DE_VOTRE_DEPOT]
    cd [NOM_DU_DOSSIER]
    ```

3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancer le simulateur** :
    ```bash
    python main.py
    ```

## 6. Architecture du Rover : Le standard URDF
Pour garantir la flexibilité et le réalisme, RoverX Lab s'appuie sur le format **URDF**. Le workflow est le suivant :

1.  **Conception CAO** : Le rover est modélisé dans un logiciel de CAO (ex: Onshape, SolidWorks, Fusion 360).
2.  **Export URDF** : Le modèle est exporté en utilisant un outil comme [`onshape-to-robot`](https://onshape-to-robot.readthedocs.io/en/latest/). Ce processus génère un fichier `rover.urdf` et les modèles 3D (`.stl`) de chaque pièce.
3.  **Chargement dans le Simulateur** : Le fichier `main.py` lance la simulation et la classe `Rover` (`rover.py`) se charge de lire le fichier URDF pour construire le rover pièce par pièce, en créant les bonnes articulations.

Ce découplage entre la conception et la simulation est au cœur de la vision du projet.

## 7. Vision Future
La version actuelle est une base solide. Les prochaines grandes étapes se concentrent sur :

* **Développement de l'API de Contrôle** :
    * Exposer des fonctions Python pour contrôler les articulations individuellement (ex: `rover.set_joint_speed('wheel_left_front_joint', 5.0)`).
* **Développement de l'API Capteurs** :
    * Simuler des capteurs virtuels (caméras, LiDAR, IMU) dont les données seront accessibles via l'API pour alimenter les algorithmes de navigation.
* **Amélioration de la Physique** :
    * Implémenter la cinématique complète des suspensions (ex: Rocker-bogie) dans la fonction `update`.
    * Gérer le patinage et le glissement des roues en fonction de la pente et du type de sol.