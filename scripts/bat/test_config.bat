@echo off
:: ============================================================
:: Projet      : GW2 Command Center
:: Fichier     : scripts\bat\test_config.bat
:: Rôle        : Lance le menu localisé de vérification des configurations Python
:: Auteur      : William CROCHOT (MisterWalky)
:: Référence   : https://github.com/MisterWalky/gw2-command-center
:: Licence     : MIT
:: ============================================================
::
:: ------------------------------------------------------------
:: DESCRIPTION
:: ------------------------------------------------------------
:: Ce script affiche un menu localisé permettant de verifier le
:: chargement des modules de configuration du projet.
::
:: Il s'appuie sur le noyau i18n du dashboard pour charger les
:: libelles utilisateur, puis appelle :
:: - py -m config.config_base
:: - py -m config.config_test
:: - py -m config.config_prod
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

call :I18N_GET "TEST_CONFIG_MENU_UI.CURRENT_DIR_LABEL" UI_CURRENT_DIR_LABEL
call :I18N_GET "TEST_CONFIG_MENU_UI.DATE_LABEL" UI_DATE_LABEL
call :I18N_GET "TEST_CONFIG_MENU_UI.TIME_LABEL" UI_TIME_LABEL
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_BASE" UI_OPTION_BASE
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_BASE_DESC" UI_OPTION_BASE_DESC
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_TEST" UI_OPTION_TEST
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_TEST_DESC" UI_OPTION_TEST_DESC
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_PROD" UI_OPTION_PROD
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_PROD_DESC" UI_OPTION_PROD_DESC
call :I18N_GET "TEST_CONFIG_MENU_UI.OPTION_ALL" UI_OPTION_ALL
call :I18N_GET "TEST_CONFIG_MENU_UI.QUIT_OPTION" UI_QUIT_OPTION
call :I18N_GET "TEST_CONFIG_MENU_UI.PROMPT_CHOICE" UI_PROMPT_CHOICE
call :I18N_GET "TEST_CONFIG_MENU_UI.INVALID_CHOICE" UI_INVALID_CHOICE

echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.TITLE"
echo =====================================
echo.
echo %UI_CURRENT_DIR_LABEL%
echo %CD%
echo.
echo %UI_DATE_LABEL% %date%
echo %UI_TIME_LABEL% %time%
echo.
echo %UI_OPTION_BASE%
echo     %UI_OPTION_BASE_DESC%
echo.
echo %UI_OPTION_TEST%
echo     %UI_OPTION_TEST_DESC%
echo.
echo %UI_OPTION_PROD%
echo     %UI_OPTION_PROD_DESC%
echo.
echo %UI_OPTION_ALL%
echo.
echo %UI_QUIT_OPTION%
echo.

set /p "CHOICE=%UI_PROMPT_CHOICE% "
set "CHOICE=%CHOICE:~0,1%"

if /I "%CHOICE%"=="Q" goto END
if "%CHOICE%"=="1" goto CONFIRM_BASE
if "%CHOICE%"=="2" goto CONFIRM_TEST
if "%CHOICE%"=="3" goto CONFIRM_PROD
if "%CHOICE%"=="4" goto CONFIRM_ALL

echo.
echo %UI_INVALID_CHOICE%
pause
goto MENU_START


:: ------------------------------------------------------------
:: CONFIRMATIONS
:: ------------------------------------------------------------

:CONFIRM_BASE
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_TITLE"
echo =====================================
echo.
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_RUN_LABEL"
echo   py -m config.config_base
echo.

call :I18N_GET "TEST_CONFIG_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_BASE


:CONFIRM_TEST
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_TITLE"
echo =====================================
echo.
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_RUN_LABEL"
echo   py -m config.config_test
echo.

call :I18N_GET "TEST_CONFIG_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_TEST


:CONFIRM_PROD
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_TITLE"
echo =====================================
echo.
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_RUN_LABEL"
echo   py -m config.config_prod
echo.

call :I18N_GET "TEST_CONFIG_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_PROD


:CONFIRM_ALL
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_TITLE"
echo =====================================
echo.
call :I18N_ECHO "TEST_CONFIG_MENU_UI.CONFIRM_RUN_SEQUENCE_LABEL"
echo   py -m config.config_base
echo   py -m config.config_test
echo   py -m config.config_prod
echo.

call :I18N_GET "TEST_CONFIG_MENU_UI.CONFIRM_PROMPT" UI_CONFIRM_PROMPT
choice /C YNQ /M "%UI_CONFIRM_PROMPT%"
if errorlevel 3 goto END
if errorlevel 2 goto MENU_START
if errorlevel 1 goto RUN_ALL


:: ------------------------------------------------------------
:: EXECUTIONS
:: ------------------------------------------------------------

:RUN_BASE
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_BASE_TITLE"
echo =====================================
echo.

py -m config.config_base
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause
goto MENU_START


:RUN_TEST
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_TEST_TITLE"
echo =====================================
echo.

py -m config.config_test
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause
goto MENU_START


:RUN_PROD
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_PROD_TITLE"
echo =====================================
echo.

py -m config.config_prod
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause
goto MENU_START


:RUN_ALL
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_BASE_TITLE"
echo =====================================
echo.

py -m config.config_base
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause

cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_TEST_TITLE"
echo =====================================
echo.

py -m config.config_test
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause

cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_PROD_TITLE"
echo =====================================
echo.

py -m config.config_prod
if errorlevel 1 goto RUN_ERROR

echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.SUCCESS_TITLE"
echo =====================================
pause

goto MENU_START


:: ------------------------------------------------------------
:: ERREUR D'EXECUTION
:: ------------------------------------------------------------

:RUN_ERROR
echo.
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.ERROR_TITLE"
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.RUN_FAILED"
pause
goto MENU_START


:: ------------------------------------------------------------
:: SORTIE
:: ------------------------------------------------------------

:END
cls
echo =====================================
call :I18N_ECHO "TEST_CONFIG_MENU_UI.EXIT_TITLE"
echo =====================================
endlocal
exit /b 0
