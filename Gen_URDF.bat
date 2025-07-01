@echo off
REM Obtained at https://dev-portal.onshape.com/keys
echo Configuration des cles API Onshape pour cette session...

set ONSHAPE_API=https://cad.onshape.com
set ONSHAPE_ACCESS_KEY=zzNkLLcBiHStX8lgwrEbqhKD
set ONSHAPE_SECRET_KEY=a0yHwEfMGBMrpGXcMrllJTg33H5K5x5ocWaOwoMFfQtq6wsE

echo.
echo Variables configurees. Vous pouvez maintenant lancer la commande onshape-to-robot.
echo.

onshape-to-robot my-robot

pause
