@echo off
:: ============================================================
:: Projet      : GW2 Command Center
:: Fichier     : dashboard\core\load_lang.bat
:: Role        : Noyau central de gestion multilingue
:: Auteur      : William CROCHOT (MisterWalky)
:: Reference   : https://github.com/MisterWalky/gw2-command-center
:: Licence     : MIT
:: ============================================================
::
:: DESCRIPTION
:: -----------
:: Ce script centralise le chargement des fichiers de langue JSON.
::
:: Il permet de :
:: - initialiser la langue active
:: - resoudre le fichier JSON a utiliser
:: - lire une cle hierarchique
:: - stocker une valeur dans une variable
:: - afficher directement une valeur
:: - tester l'existence d'une cle
::
:: CONVENTIONS RETENUES
:: --------------------
:: - Les commentaires du code restent en francais pendant le
::   developpement local.
:: - Les messages systeme critiques affiches dans la console
::   restent en anglais.
:: - Les fichiers de langue sont en JSON et utilisent une
::   structure hierarchique.
:: - Les cles sont appelees sous forme de chemin :
::     MENU.MAIN
::     INPUT.YOUR_CHOICE
::     HELP.OBJECTIVE_LINES.0
::
:: STRATEGIE DE RESOLUTION DES LANGUES
:: ----------------------------------
:: 1. Tenter la langue demandee
:: 2. Sinon basculer sur l'anglais (en.json)
:: 3. Sinon arreter l'application avec une erreur critique
::
:: EXEMPLES D'UTILISATION
:: ----------------------
::   call "dashboard\core\load_lang.bat" init fr
::
::   call "dashboard\core\load_lang.bat" get MENU.MAIN LABEL_MAIN
::   echo %LABEL_MAIN%
::
::   call "dashboard\core\load_lang.bat" echo MENU.MAIN
::
::   call "dashboard\core\load_lang.bat" exists MENU.MAIN KEY_FOUND
::   if "%KEY_FOUND%"=="1" echo Key found
::
:: DEPENDANCES
:: -----------
:: - PowerShell est utilise pour lire les fichiers JSON.
::
:: VARIABLES EXPOSEES
:: ------------------
:: - I18N_LANG  : code langue actif
:: - I18N_FILE  : chemin absolu du fichier JSON charge
::
:: REMARQUE
:: --------
:: Ce script est concu pour etre appele avec "call".
:: ============================================================

goto :MAIN


:: ------------------------------------------------------------
:: POINT D'ENTREE
:: ------------------------------------------------------------

:MAIN
if /I "%~1"=="init"   goto :CMD_INIT
if /I "%~1"=="get"    goto :CMD_GET
if /I "%~1"=="echo"   goto :CMD_ECHO
if /I "%~1"=="exists" goto :CMD_EXISTS
if /I "%~1"=="help"   goto :CMD_HELP
goto :CMD_HELP


:: ------------------------------------------------------------
:: COMMANDE : INIT
:: ------------------------------------------------------------
:: Initialise le systeme de langue.
::
:: Usage :
::   call load_lang.bat init fr
::
:: Resultat :
::   - I18N_LANG est defini
::   - I18N_FILE est defini
::
:: Comportement :
::   - si la langue demandee existe, elle est chargee
::   - sinon fallback automatique vers en.json
::   - si en.json n'existe pas non plus, erreur critique
:: ------------------------------------------------------------

:CMD_INIT
set "REQUESTED_LANG=%~2"
if not defined REQUESTED_LANG set "REQUESTED_LANG=en"

call :RESOLVE_LANGUAGE_FILE "%REQUESTED_LANG%"
if errorlevel 1 exit /b 1

exit /b 0


:: ------------------------------------------------------------
:: COMMANDE : GET
:: ------------------------------------------------------------
:: Lit une cle de langue et la stocke dans une variable.
::
:: Usage :
::   call load_lang.bat get MENU.MAIN LABEL_MAIN
::   echo %LABEL_MAIN%
:: ------------------------------------------------------------

:CMD_GET
set "KEY_PATH=%~2"
set "OUTPUT_VAR=%~3"

if not defined KEY_PATH (
    echo [ERROR] Missing key path for GET command.
    exit /b 1
)

if not defined OUTPUT_VAR (
    echo [ERROR] Missing output variable for GET command.
    exit /b 1
)

call :ENSURE_LANGUAGE_READY
if errorlevel 1 exit /b 1

call :READ_JSON_KEY "%I18N_FILE%" "%KEY_PATH%" "%OUTPUT_VAR%"
if errorlevel 1 (
    echo [ERROR] Unable to read language key "%KEY_PATH%".
    exit /b 1
)

exit /b 0


:: ------------------------------------------------------------
:: COMMANDE : ECHO
:: ------------------------------------------------------------
:: Lit une cle de langue et l'affiche directement.
::
:: Usage :
::   call load_lang.bat echo MENU.MAIN
:: ------------------------------------------------------------

:CMD_ECHO
set "KEY_PATH=%~2"

if not defined KEY_PATH (
    echo [ERROR] Missing key path for ECHO command.
    exit /b 1
)

call :ENSURE_LANGUAGE_READY
if errorlevel 1 exit /b 1

call :READ_JSON_KEY "%I18N_FILE%" "%KEY_PATH%" "__I18N_ECHO_VALUE__"
if errorlevel 1 (
    echo [ERROR] Unable to read language key "%KEY_PATH%".
    exit /b 1
)

echo %__I18N_ECHO_VALUE__%
set "__I18N_ECHO_VALUE__="
exit /b 0


:: ------------------------------------------------------------
:: COMMANDE : EXISTS
:: ------------------------------------------------------------
:: Teste l'existence d'une cle dans le fichier de langue actif.
::
:: Usage :
::   call load_lang.bat exists MENU.MAIN KEY_FOUND
::
:: Resultat :
::   KEY_FOUND=1 si la cle existe
::   KEY_FOUND=0 sinon
:: ------------------------------------------------------------

:CMD_EXISTS
set "KEY_PATH=%~2"
set "OUTPUT_VAR=%~3"

if not defined KEY_PATH (
    echo [ERROR] Missing key path for EXISTS command.
    exit /b 1
)

if not defined OUTPUT_VAR (
    echo [ERROR] Missing output variable for EXISTS command.
    exit /b 1
)

call :ENSURE_LANGUAGE_READY
if errorlevel 1 exit /b 1

call :READ_JSON_KEY "%I18N_FILE%" "%KEY_PATH%" "__I18N_EXISTS_VALUE__"
if errorlevel 1 (
    set "%OUTPUT_VAR%=0"
    exit /b 0
)

set "%OUTPUT_VAR%=1"
set "__I18N_EXISTS_VALUE__="
exit /b 0


:: ------------------------------------------------------------
:: AIDE
:: ------------------------------------------------------------

:CMD_HELP
echo.
echo ============================================================
echo HELP - load_lang.bat
echo ============================================================
echo.
echo Available commands:
echo.
echo   init   [lang]
echo          Initialize the active language.
echo          Example: call load_lang.bat init fr
echo.
echo   get    [key] [variable]
echo          Read a key and store the value in a variable.
echo          Example: call load_lang.bat get MENU.MAIN LABEL_MAIN
echo.
echo   echo   [key]
echo          Print a language value directly.
echo          Example: call load_lang.bat echo MENU.MAIN
echo.
echo   exists [key] [variable]
echo          Store 1 if the key exists, otherwise 0.
echo          Example: call load_lang.bat exists MENU.MAIN FOUND
echo.
echo Expected key format:
echo   MENU.MAIN
echo   INPUT.YOUR_CHOICE
echo   HELP.OBJECTIVE_LINES.0
echo.
exit /b 0


:: ------------------------------------------------------------
:: RESOLUTION DU FICHIER DE LANGUE
:: ------------------------------------------------------------
:: Cette routine applique la logique de fallback :
:: - langue demandee
:: - anglais
:: - erreur critique si rien n'existe
:: ------------------------------------------------------------

:RESOLVE_LANGUAGE_FILE
set "REQUESTED_LANG=%~1"
if not defined REQUESTED_LANG set "REQUESTED_LANG=en"

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\i18n") do set "I18N_DIR=%%~fI"

set "REQUESTED_FILE=%I18N_DIR%\%REQUESTED_LANG%.json"
set "FALLBACK_LANG=en"
set "FALLBACK_FILE=%I18N_DIR%\%FALLBACK_LANG%.json"

if exist "%REQUESTED_FILE%" (
    set "I18N_LANG=%REQUESTED_LANG%"
    set "I18N_FILE=%REQUESTED_FILE%"
    exit /b 0
)

if /I not "%REQUESTED_LANG%"=="%FALLBACK_LANG%" (
    if exist "%FALLBACK_FILE%" (
        echo [WARNING] Language file "%REQUESTED_LANG%.json" was not found. Falling back to English.
        set "I18N_LANG=%FALLBACK_LANG%"
        set "I18N_FILE=%FALLBACK_FILE%"
        exit /b 0
    )
)

if exist "%FALLBACK_FILE%" (
    set "I18N_LANG=%FALLBACK_LANG%"
    set "I18N_FILE=%FALLBACK_FILE%"
    exit /b 0
)

echo [ERROR] No valid language file could be loaded.
echo [ERROR] The application cannot continue without a language file.
echo [ERROR] Expected files:
echo [ERROR]   "%REQUESTED_FILE%"
echo [ERROR]   "%FALLBACK_FILE%"
echo [ERROR] Restore at least one valid language file in the i18n directory.
echo [ERROR] For support, refer to:
echo [ERROR]   https://github.com/MisterWalky/gw2-command-center
exit /b 1


:: ------------------------------------------------------------
:: VERIFICATION DE L'INITIALISATION
:: ------------------------------------------------------------
:: Garantit qu'une langue active et un fichier valide existent.
:: Si rien n'est initialise, tente un chargement implicite en
:: anglais.
:: ------------------------------------------------------------

:ENSURE_LANGUAGE_READY
if defined I18N_FILE (
    if exist "%I18N_FILE%" (
        exit /b 0
    )
)

call :RESOLVE_LANGUAGE_FILE "en"
if errorlevel 1 exit /b 1

if not defined I18N_FILE (
    echo [ERROR] Language system initialization failed.
    exit /b 1
)

if not exist "%I18N_FILE%" (
    echo [ERROR] Active language file is missing: "%I18N_FILE%"
    exit /b 1
)

exit /b 0


:: ------------------------------------------------------------
:: LECTURE D'UNE CLE JSON
:: ------------------------------------------------------------
:: Lit une cle hierarchique dans un fichier JSON et retourne la
:: valeur dans la variable passee en 3e argument.
::
:: Exemple :
::   call :READ_JSON_KEY "...\fr.json" "MENU.MAIN" RESULT
::
:: Particularites :
:: - gere les objets imbriques
:: - gere les index de tableaux
:: - ex : HELP.OBJECTIVE_LINES.0
:: - preserve mieux les caracteres speciaux via un fichier
::   temporaire intermediaire
:: ------------------------------------------------------------

:READ_JSON_KEY
setlocal DisableDelayedExpansion

set "JSON_FILE=%~1"
set "KEY_PATH=%~2"
set "RETURN_VAR=%~3"
set "TMP_OUTPUT=%TEMP%\gw2cc_i18n_%RANDOM%_%RANDOM%.tmp"

if not exist "%JSON_FILE%" (
    endlocal & exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass ^
    "$ErrorActionPreference = 'Stop';" ^
    "$jsonPath = '%JSON_FILE%';" ^
    "$path = '%KEY_PATH%';" ^
    "$outFile = '%TMP_OUTPUT%';" ^
    "$data = Get-Content -Raw -Encoding UTF8 $jsonPath | ConvertFrom-Json;" ^
    "$value = $data;" ^
    "foreach ($part in $path.Split('.')) {" ^
    "    if ($part -match '^\d+$') {" ^
    "        $index = [int]$part;" ^
    "        if ($null -eq $value) { throw 'INDEX_NOT_FOUND' }" ^
    "        if ($value.Count -le $index) { throw 'INDEX_NOT_FOUND' }" ^
    "        $value = $value[$index];" ^
    "    } else {" ^
    "        if ($null -eq $value) { throw 'KEY_NOT_FOUND' }" ^
    "        $prop = $value.PSObject.Properties[$part];" ^
    "        if ($null -eq $prop) { throw 'KEY_NOT_FOUND' }" ^
    "        $value = $prop.Value;" ^
    "    }" ^
    "}" ^
    "if ($null -eq $value) { throw 'EMPTY_VALUE' }" ^
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8;" ^
    "Set-Content -Path $outFile -Value ([string]$value) -Encoding UTF8"
if errorlevel 1 (
    if exist "%TMP_OUTPUT%" del /q "%TMP_OUTPUT%" >nul 2>&1
    endlocal & exit /b 1
)

if not exist "%TMP_OUTPUT%" (
    endlocal & exit /b 1
)

for /f "usebackq delims=" %%A in ("%TMP_OUTPUT%") do (
    del /q "%TMP_OUTPUT%" >nul 2>&1
    endlocal & set "%RETURN_VAR%=%%A" & exit /b 0
)

del /q "%TMP_OUTPUT%" >nul 2>&1
endlocal & exit /b 1
