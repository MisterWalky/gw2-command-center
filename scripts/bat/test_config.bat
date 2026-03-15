@echo off
:: ------------------------------------------------------------
:: test_config.bat
::
:: Script de verification des fichiers de configuration.
::
:: Options disponibles :
::
:: 1 - CONFIG_BASE
::     Charge config_base.py et affiche les parametres communs.
::
:: 2 - CONFIG_TEST
::     Charge config_test.py et affiche les parametres
::     specifiques a l'environnement TEST.
::
:: 3 - CONFIG_PROD
::     Charge config_prod.py et affiche les parametres
::     specifiques a l'environnement PROD.
::
:: 4 - Les 3 a la suite
::     Lance les trois tests successivement.
::
:: Ce script permet de verifier rapidement que les fichiers de
:: configuration se chargent correctement avant d'utiliser les
:: autres scripts du projet.
:: ------------------------------------------------------------

setlocal EnableDelayedExpansion

:: Retour a la racine du projet
cd /d "%~dp0\..\.."

:MENU_START
cls
echo =====================================
echo GW2 API - TEST CONFIGURATIONS
echo =====================================
echo.
echo Dossier courant :
echo %CD%
echo.
echo Date : %date%
echo Heure : %time%
echo.
echo 1 - Tester CONFIG_BASE
echo     Charge config.config_base
echo.
echo 2 - Tester CONFIG_TEST
echo     Charge config.config_test
echo.
echo 3 - Tester CONFIG_PROD
echo     Charge config.config_prod
echo.
echo 4 - Tester les 3 a la suite
echo.
echo Q - Quitter
echo.

set /p CHOICE=Votre choix : 
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto CONFIRM_BASE
if "%CHOICE%"=="2" goto CONFIRM_TEST
if "%CHOICE%"=="3" goto CONFIRM_PROD
if "%CHOICE%"=="4" goto CONFIRM_ALL

echo.
echo Choix invalide.
pause
goto MENU_START


:CONFIRM_BASE
cls
echo =====================================
echo CONFIRMATION
echo =====================================
echo.
echo Vous allez lancer :
echo   py -m config.config_base
echo.
choice /C YNQ /M "Confirmer"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_BASE


:CONFIRM_TEST
cls
echo =====================================
echo CONFIRMATION
echo =====================================
echo.
echo Vous allez lancer :
echo   py -m config.config_test
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
echo   py -m config.config_prod
echo.
choice /C YNQ /M "Confirmer"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_PROD


:CONFIRM_ALL
cls
echo =====================================
echo CONFIRMATION
echo =====================================
echo.
echo Vous allez lancer successivement :
echo   py -m config.config_base
echo   py -m config.config_test
echo   py -m config.config_prod
echo.
choice /C YNQ /M "Confirmer"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_ALL


:RUN_BASE
cls
echo =====================================
echo TEST CONFIG_BASE
echo =====================================
echo.
py -m config.config_base
echo.
pause
goto MENU_START


:RUN_TEST
cls
echo =====================================
echo TEST CONFIG_TEST
echo =====================================
echo.
py -m config.config_test
echo.
pause
goto MENU_START


:RUN_PROD
cls
echo =====================================
echo TEST CONFIG_PROD
echo =====================================
echo.
py -m config.config_prod
echo.
pause
goto MENU_START


:RUN_ALL
cls
echo =====================================
echo TEST CONFIG_BASE
echo =====================================
echo.
py -m config.config_base
echo.
pause

cls
echo =====================================
echo TEST CONFIG_TEST
echo =====================================
echo.
py -m config.config_test
echo.
pause

cls
echo =====================================
echo TEST CONFIG_PROD
echo =====================================
echo.
py -m config.config_prod
echo.
pause

goto MENU_START


:END
cls
echo =====================================
echo FIN DES TESTS
echo =====================================
pause
endlocal