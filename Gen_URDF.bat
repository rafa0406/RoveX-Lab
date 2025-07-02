@echo off
REM Obtained at https://dev-portal.onshape.com/keys
echo Configuration des cles API Onshape pour cette session...

set ONSHAPE_API=https://cad.onshape.com
set ONSHAPE_ACCESS_KEY=6lVVVklNbZZRcFsz4WeBDfjN
set ONSHAPE_SECRET_KEY=Lc7GlN4GO1O7C6tpOYXY2Nc4RBbgB8uwGVUkIMMmwCOLePuZ

echo ONSHAPE_API : %ONSHAPE_API%
echo ONSHAPE_ACCESS_KEY : %ONSHAPE_ACCESS_KEY%
echo ONSHAPE_SECRET_KEY : %ONSHAPE_SECRET_KEY%
echo.
echo Variables configurees.
echo.

REM Creation de l'environnement virtuel Python
python -m venv my_robot_env

REM Lancement du script de création du fichier URDF
onshape-to-robot my-robot

