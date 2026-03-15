@echo off
:: ------------------------------------------------------------
:: launch_sync.bat
::
:: Lance le menu de synchronisation du projet GW2 API.
::
:: Ce script appelle :
::     py scripts/python/run_sync_menu.py
::
:: Le menu Python permet de :
:: - choisir TEST ou PROD
:: - synchroniser tous les endpoints SNAPSHOT
:: - synchroniser tous les endpoints TIMESERIES
:: - synchroniser SNAPSHOT + TIMESERIES
:: - synchroniser un seul endpoint
::
:: Un resume final est affiche avant execution.
:: ------------------------------------------------------------

setlocal

:: Retour a la racine du projet
cd /d "%~dp0\..\.."

:MENU_START
cls
echo =====================================
echo GW2 API - LANCEUR DE SYNCHRONISATION
echo =====================================
echo.
echo Dossier courant :
echo %CD%
echo.
echo Date : %date%
echo Heure : %time%
echo.
echo 1 - Lancer le menu de synchronisation
echo     Ouvre le menu interactif Python.
echo.
echo Q - Quitter
echo.

set /p CHOICE=Votre choix : 
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto CONFIRM_RUN

echo.
echo Choix invalide.
pause
goto MENU_START


:CONFIRM_RUN
cls
echo =====================================
echo CONFIRMATION
echo =====================================
echo.
echo Vous allez lancer :
echo   py scripts/run_sync_menu.py
echo.
choice /C YNQ /M "Confirmer"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_SYNC_MENU


:RUN_SYNC_MENU
cls
echo =====================================
echo MENU DE SYNCHRONISATION
echo =====================================
echo.
py scripts/run_sync_menu.py
echo.
echo =====================================
echo RETOUR AU LANCEUR
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