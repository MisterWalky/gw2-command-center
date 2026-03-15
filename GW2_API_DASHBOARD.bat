@echo off
setlocal EnableDelayedExpansion
pushd "%~dp0"

:: ============================================================
:: GW2_API_DASHBOARD.bat
::
:: Dashboard principal du projet GW2 API.
::
:: Ce script affiche un tableau de bord console permettant de :
:: - visualiser la configuration API
:: - lister les endpoints configurés
:: - consulter les dernières synchronisations
:: - surveiller l'état des bases SQLite
:: - accéder aux scripts utilitaires du projet
::
:: Organisation :
:: 1 - Menu principal
:: 2 - Tableau de bord
:: 3 - Actions
:: 4 - Aide
:: 5 - Langue
::
:: Scripts Python appelés :
:: - scripts\python\api_status.py
:: - scripts\python\endpoints_status.py
:: - scripts\python\sync_status.py
:: - scripts\python\db_status.py
::
:: Scripts batch accessibles :
:: - scripts\bat\test_config.bat
:: - scripts\bat\init_db.bat
:: - scripts\bat\launch_sync.bat
:: ============================================================


:: ------------------------------------------------------------
:: CONFIGURATION LANGUE
:: ------------------------------------------------------------

if not defined APP_LANG set "APP_LANG=fr"
call :LOAD_LANG


:: ------------------------------------------------------------
:: CHEMINS DES BASES
:: ------------------------------------------------------------

set "TEST_DB=databases\GW2_TEST.db"
set "PROD_DB=databases\GW2_API.db"


:: ------------------------------------------------------------
:: HORODATAGE DE LANCEMENT
:: ------------------------------------------------------------

set "RAW_TIME=%time: =0%"
set "START_TIME=%RAW_TIME:~0,8%"

for /f "tokens=1-3 delims=/" %%a in ("%date%") do (
    set "START_DAY=%%a"
    set "START_MONTH=%%b"
    set "START_YEAR=%%c"
)

set "START_DATETIME=%START_YEAR%-%START_MONTH%-%START_DAY% %START_TIME%"

call :TIME_TO_SECONDS "%START_TIME%" SESSION_START_SECONDS


:: ------------------------------------------------------------
:: MENU PRINCIPAL
:: ------------------------------------------------------------

:MENU_MAIN
cls
call :PRINT_HEADER "%TXT_APP_TITLE%"
echo.
echo %TXT_PROJECT%  : Dashboard ETL / SQLite / Guild Wars 2
echo %TXT_FOLDER%   : %CD%
echo %TXT_STARTED%  : %START_DATETIME%
echo %TXT_LANGUAGE% : %TXT_LANG_NAME%
echo.
echo  1 - %TXT_DASHBOARD%
echo  2 - %TXT_ACTIONS%
echo  3 - %TXT_HELP%
echo  4 - %TXT_LANGUAGE_MENU%
echo.
echo  Q - %TXT_EXIT%
echo.

set /p CHOICE=%TXT_YOUR_CHOICE%
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto MENU_DASHBOARD
if "%CHOICE%"=="2" goto MENU_ACTIONS
if "%CHOICE%"=="3" goto SHOW_HELP
if "%CHOICE%"=="4" goto MENU_LANGUAGE

echo.
echo %TXT_INVALID_CHOICE%
pause
goto MENU_MAIN


:: ------------------------------------------------------------
:: MENU TABLEAU DE BORD
:: ------------------------------------------------------------

:MENU_DASHBOARD
cls
call :PRINT_HEADER "%TXT_DASHBOARD%"
echo.
echo  1 - %TXT_FULL_VIEW%
echo  2 - %TXT_HOME%
echo  3 - %TXT_API_CONFIG%
echo  4 - %TXT_ENDPOINTS%
echo  5 - %TXT_SYNC%
echo  6 - %TXT_DB_STATE%
echo.
echo  R - %TXT_BACK%
echo  Q - %TXT_EXIT%
echo.

set /p CHOICE=%TXT_YOUR_CHOICE%
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if /I "%CHOICE%"=="R" goto MENU_MAIN
if "%CHOICE%"=="1" goto DASHBOARD_FULL
if "%CHOICE%"=="2" goto DASHBOARD_HOME
if "%CHOICE%"=="3" goto DASHBOARD_API
if "%CHOICE%"=="4" goto DASHBOARD_ENDPOINTS
if "%CHOICE%"=="5" goto DASHBOARD_SYNC
if "%CHOICE%"=="6" goto DASHBOARD_DB

echo.
echo %TXT_INVALID_CHOICE%
pause
goto MENU_DASHBOARD


:: ------------------------------------------------------------
:: MENU ACTIONS
:: ------------------------------------------------------------

:MENU_ACTIONS
cls
call :PRINT_HEADER "%TXT_ACTIONS%"
echo.
echo  1 - %TXT_TEST_CONFIG%
echo  2 - %TXT_INIT_DB%
echo  3 - %TXT_LAUNCH_SYNC%
echo.
echo  R - %TXT_BACK%
echo  Q - %TXT_EXIT%
echo.

set /p CHOICE=%TXT_YOUR_CHOICE%
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if /I "%CHOICE%"=="R" goto MENU_MAIN
if "%CHOICE%"=="1" goto RUN_CONFIG
if "%CHOICE%"=="2" goto RUN_INIT_DB
if "%CHOICE%"=="3" goto RUN_SYNC

echo.
echo %TXT_INVALID_CHOICE%
pause
goto MENU_ACTIONS


:: ------------------------------------------------------------
:: MENU LANGUE
:: ------------------------------------------------------------
:: Actuellement une seule langue active (FR)
:: Le système reste prévu pour supporter plusieurs langues
:: dans le futur.

:MENU_LANGUAGE
cls
call :PRINT_HEADER "%TXT_LANGUAGE_MENU%"
echo.
echo  1 - Francais
echo.
echo  R - %TXT_BACK%
echo  Q - %TXT_EXIT%
echo.

set /p CHOICE=%TXT_YOUR_CHOICE%
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if /I "%CHOICE%"=="R" goto MENU_MAIN
if "%CHOICE%"=="1" set "APP_LANG=fr" & call :LOAD_LANG & goto MENU_MAIN

echo.
echo %TXT_INVALID_CHOICE%
pause
goto MENU_LANGUAGE


:: ------------------------------------------------------------
:: AFFICHAGE : EN-TETE STANDARD
:: ------------------------------------------------------------

:PRINT_HEADER
echo ===============================================================
echo %~1
echo ===============================================================
exit /b


:: ------------------------------------------------------------
:: CHARGEMENT DE LA LANGUE
:: ------------------------------------------------------------
:: Charge le fichier de traduction correspondant à APP_LANG
:: Les fichiers sont situés dans dashboard\i18n

:LOAD_LANG
if exist "dashboard\i18n\%APP_LANG%.bat" (
    call "dashboard\i18n\%APP_LANG%.bat"
) else (
    set "APP_LANG=fr"
    call "dashboard\i18n\fr.bat"
)
exit /b
