@echo off
:: ============================================================
:: Projet      : GW2 Command Center
:: Fichier     : scripts\bat\launch_sync.bat
:: Rôle        : Lance le menu batch localisé d'accès à la synchronisation
:: Auteur      : William CROCHOT (MisterWalky)
:: Référence   : https://github.com/MisterWalky/gw2-command-center
:: Licence     : MIT
:: ============================================================
::
:: ------------------------------------------------------------
:: DESCRIPTION
:: ------------------------------------------------------------
:: Ce script affiche un menu localisé permettant d'ouvrir le
:: menu Python de synchronisation du projet.
::
:: Il s'appuie sur le noyau i18n du dashboard pour charger les
:: libelles utilisateur, puis appelle :
:: - py scripts/python/run_sync_menu.py
::
:: Les messages techniques critiques peuvent rester en anglais
:: si le systeme de langue n'est pas disponible.
:: ------------------------------------------------------------

setlocal

cd /d "%~dp0\..\.."

if not defined APP_LANG set "APP_LANG=en"

call "dashboard\core\load_lang.bat" init "%APP_LANG%"
if errorlevel 1 (
    echo [ERROR] Failed to initialize language system.
    pause
    exit /b 1
)

goto :MENU_START


:: ------------------------------------------------------------
:: RACCOURCIS I18N
:: ------------------------------------------------------------

:I18N_GET
call "dashboard\core\load_lang.bat" get "%~1" "%~2"
exit /b %errorlevel%

:I18N_ECHO
call "dashboard\core\load_lang.bat" echo "%~1"
exit /b %errorlevel%


:: ------------------------------------------------------------
:: MENU PRINCIPAL
:: ------------------------------------------------------------

:MENU_START
cls

call :I18N_GET "LAUNCH_SYNC_MENU_UI.TITLE" UI_TITLE
call :I18N_GET "LAUNCH_SYNC_MENU_UI.CURRENT_DIR_LABEL" UI_CURRENT_DIR_LABEL
call :I18N_GET "LAUNCH_SYNC_MENU_UI.DATE_LABEL" UI_DATE_LABEL
call :I18N_GET "LAUNCH_SYNC_MENU_UI.TIME_LABEL" UI_TIME_LABEL
call :I18N_GET "LAUNCH_SYNC_MENU_UI.RUN_OPTION" UI_RUN_OPTION
call :I18N_GET "LAUNCH_SYNC_MENU_UI.RUN_DESCRIPTION" UI_RUN_DESCRIPTION
call :I18N_GET "LAUNCH_SYNC_MENU_UI.QUIT_OPTION" UI_QUIT_OPTION
call :I18N_GET "LAUNCH_SYNC_MENU_UI.PROMPT_CHOICE" UI_PROMPT_CHOICE
call :I18N_GET "LAUNCH_SYNC_MENU_UI.INVALID_CHOICE" UI_INVALID_CHOICE

echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.TITLE"
echo =====================================
echo.
echo %UI_CURRENT_DIR_LABEL%
echo %CD%
echo.
echo %UI_DATE_LABEL% %date%
echo %UI_TIME_LABEL% %time%
echo.
echo %UI_RUN_OPTION%
echo     %UI_RUN_DESCRIPTION%
echo.
echo %UI_QUIT_OPTION%
echo.

set /p "CHOICE=%UI_PROMPT_CHOICE% "
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto CONFIRM_RUN

echo.
echo %UI_INVALID_CHOICE%
pause
goto MENU_START


:: ------------------------------------------------------------
:: CONFIRMATION
:: ------------------------------------------------------------

:CONFIRM_RUN
cls
echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.CONFIRM_TITLE"
echo =====================================
echo.
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.CONFIRM_RUN_LABEL"
echo   py scripts/python/run_sync_menu.py
echo.

call :I18N_GET "LAUNCH_SYNC_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_SYNC_MENU


:: ------------------------------------------------------------
:: EXECUTION
:: ------------------------------------------------------------

:RUN_SYNC_MENU
cls
echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.RUN_TITLE"
echo =====================================
echo.

py scripts/python/run_sync_menu.py
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.RETURN_TITLE"
echo =====================================
pause
goto MENU_START


:: ------------------------------------------------------------
:: ERREUR D'EXECUTION
:: ------------------------------------------------------------

:RUN_ERROR
echo.
echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.ERROR_TITLE"
echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.RUN_FAILED"
pause
goto MENU_START


:: ------------------------------------------------------------
:: SORTIE
:: ------------------------------------------------------------

:END
cls
echo =====================================
call :I18N_ECHO "LAUNCH_SYNC_MENU_UI.EXIT_TITLE"
echo =====================================
endlocal
exit /b 0
