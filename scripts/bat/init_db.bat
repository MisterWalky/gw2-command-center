@echo off
:: ------------------------------------------------------------
:: init_db.bat
::
:: Script d'initialisation des bases SQLite du projet.
::
:: Options disponibles :
::
:: 1 - TEST
::     Initialise la base GW2_TEST.db
::     pour le developpement et les essais.
::
:: 2 - PRODUCTION
::     Initialise la base GW2_API.db
::     pour les synchronisations reelles.
::
:: Ce script appelle :
::     py scripts/python/init_db.py test
:: ou
::     py scripts/python/init_db.py prod
::
:: Il cree automatiquement :
:: - les tables techniques
:: - les tables definies dans ENDPOINTS
:: - les index associes
:: ------------------------------------------------------------

setlocal EnableDelayedExpansion

:: Retour a la racine du projet
cd /d "%~dp0\..\.."

:MENU_START
cls
echo =====================================
echo GW2 API - INITIALISATION BASE
echo =====================================
echo.
echo Dossier courant :
echo %CD%
echo.
echo Date : %date%
echo Heure : %time%
echo.
echo Choix de la base :
echo 1 - TEST
echo     Initialise la base de developpement.
echo.
echo 2 - PRODUCTION
echo     Initialise la base de production.
echo.
echo Q - Quitter
echo.

set /p CHOICE=Votre choix : 
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto CONFIRM_TEST
if "%CHOICE%"=="2" goto CONFIRM_PROD

echo.
echo Choix invalide.
pause
goto MENU_START


:CONFIRM_TEST
cls
echo =====================================
echo CONFIRMATION
echo =====================================
echo.
echo Vous allez lancer :
echo   py scripts/init_db.py test
echo.
choice /C YNQ /M "Confirmer"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_TEST


:CONFIRM_PROD
cls
echo =====================================
echo CONFIRMATION
echo =====================================
echo.
echo Vous allez lancer :
echo   py scripts/init_db.py prod
echo.
choice /C YNQ /M "Confirmer"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_PROD


:RUN_TEST
cls
echo =====================================
echo INITIALISATION BASE TEST
echo =====================================
echo.
py scripts/init_db.py test
echo.
echo =====================================
echo FIN
echo =====================================
pause
goto MENU_START


:RUN_PROD
cls
echo =====================================
echo INITIALISATION BASE PRODUCTION
echo =====================================
echo.
py scripts/init_db.py prod
echo.
echo =====================================
echo FIN
echo =====================================
pause
goto MENU_START


:END
cls
echo =====================================
echo SORTIE
echo =====================================
pause
endlocal