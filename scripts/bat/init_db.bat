@echo off
:: ============================================================
:: Projet      : GW2 Command Center
:: Fichier     : scripts\bat\init_db.bat
:: Rôle        : Lance le menu localisé d'initialisation des bases SQLite
:: Auteur      : William CROCHOT (MisterWalky)
:: Référence   : https://github.com/MisterWalky/gw2-command-center
:: Licence     : MIT
:: ============================================================
::
:: ------------------------------------------------------------
:: DESCRIPTION
:: ------------------------------------------------------------
:: Ce script affiche un menu localisé permettant de lancer
:: l'initialisation de la base SQLite en environnement test
:: ou production.
::
:: Il s'appuie sur le noyau i18n du dashboard pour charger les
:: libelles utilisateur, puis appelle :
:: - py scripts/python/init_db.py test
:: - py scripts/python/init_db.py prod
::
:: Les messages techniques critiques peuvent rester en anglais
:: si le systeme de langue n'est pas disponible.
:: ------------------------------------------------------------

setlocal EnableDelayedExpansion

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

call :I18N_GET "INIT_DB_MENU_UI.TITLE" UI_TITLE
call :I18N_GET "INIT_DB_MENU_UI.CURRENT_DIR_LABEL" UI_CURRENT_DIR_LABEL
call :I18N_GET "INIT_DB_MENU_UI.DATE_LABEL" UI_DATE_LABEL
call :I18N_GET "INIT_DB_MENU_UI.TIME_LABEL" UI_TIME_LABEL
call :I18N_GET "INIT_DB_MENU_UI.ENVIRONMENT_LABEL" UI_ENVIRONMENT_LABEL
call :I18N_GET "INIT_DB_MENU_UI.TEST_OPTION" UI_TEST_OPTION
call :I18N_GET "INIT_DB_MENU_UI.TEST_DESCRIPTION" UI_TEST_DESCRIPTION
call :I18N_GET "INIT_DB_MENU_UI.PROD_OPTION" UI_PROD_OPTION
call :I18N_GET "INIT_DB_MENU_UI.PROD_DESCRIPTION" UI_PROD_DESCRIPTION
call :I18N_GET "INIT_DB_MENU_UI.QUIT_OPTION" UI_QUIT_OPTION
call :I18N_GET "INIT_DB_MENU_UI.PROMPT_CHOICE" UI_PROMPT_CHOICE
call :I18N_GET "INIT_DB_MENU_UI.INVALID_CHOICE" UI_INVALID_CHOICE

echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.TITLE"
echo =====================================
echo.
echo %UI_CURRENT_DIR_LABEL%
echo %CD%
echo.
echo %UI_DATE_LABEL% %date%
echo %UI_TIME_LABEL% %time%
echo.
echo %UI_ENVIRONMENT_LABEL%
echo %UI_TEST_OPTION%
echo     %UI_TEST_DESCRIPTION%
echo.
echo %UI_PROD_OPTION%
echo     %UI_PROD_DESCRIPTION%
echo.
echo %UI_QUIT_OPTION%
echo.

set /p "CHOICE=%UI_PROMPT_CHOICE% "
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto CONFIRM_TEST
if "%CHOICE%"=="2" goto CONFIRM_PROD

echo.
echo %UI_INVALID_CHOICE%
pause
goto MENU_START


:: ------------------------------------------------------------
:: CONFIRMATION TEST
:: ------------------------------------------------------------

:CONFIRM_TEST
cls
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.CONFIRM_TEST_TITLE"
echo =====================================
echo.
call :I18N_ECHO "INIT_DB_MENU_UI.CONFIRM_RUN_LABEL"
echo   py scripts/python/init_db.py test
echo.

call :I18N_GET "INIT_DB_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_TEST


:: ------------------------------------------------------------
:: CONFIRMATION PRODUCTION
:: ------------------------------------------------------------

:CONFIRM_PROD
cls
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.CONFIRM_PROD_TITLE"
echo =====================================
echo.
call :I18N_ECHO "INIT_DB_MENU_UI.CONFIRM_RUN_LABEL"
echo   py scripts/python/init_db.py prod
echo.

call :I18N_GET "INIT_DB_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_PROD


:: ------------------------------------------------------------
:: EXECUTION TEST
:: ------------------------------------------------------------

:RUN_TEST
cls
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.RUN_TEST_TITLE"
echo =====================================
echo.

py scripts/python/init_db.py test
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause
goto MENU_START


:: ------------------------------------------------------------
:: EXECUTION PRODUCTION
:: ------------------------------------------------------------

:RUN_PROD
cls
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.RUN_PROD_TITLE"
echo =====================================
echo.

py scripts/python/init_db.py prod
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause
goto MENU_START


:: ------------------------------------------------------------
:: ERREUR D'EXECUTION
:: ------------------------------------------------------------

:RUN_ERROR
echo.
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.ERROR_TITLE"
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.RUN_FAILED"
pause
goto MENU_START


:: ------------------------------------------------------------
:: SORTIE
:: ------------------------------------------------------------

:END
cls
echo =====================================
call :I18N_ECHO "INIT_DB_MENU_UI.EXIT_TITLE"
echo =====================================
endlocal
exit /b 0
