@echo off
setlocal EnableExtensions
chcp 65001 >nul
set PYTHONUTF8=1
set "PASTA=%~dp0"
cd /d "%PASTA%"
title Melhores Momentos - Clipping

echo ============================================
echo   MELHORES MOMENTOS - encontrar clips
echo ============================================
echo.

rem ---------- 1. Python ----------
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [!] Python nao encontrado. A instalar com o winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    echo.
    echo Python instalado. FECHA esta janela e abre o .bat outra vez.
    pause
    exit /b
)

rem ---------- 2. ffmpeg ----------
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [!] ffmpeg nao encontrado. A instalar com o winget...
    winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    echo.
    echo ffmpeg instalado. FECHA esta janela e abre o .bat outra vez.
    pause
    exit /b
)

rem ---------- 3. Ambiente Python (so na primeira vez) ----------
if not exist "%PASTA%.venv\Scripts\python.exe" (
    echo A preparar o ambiente pela primeira vez - pode demorar alguns minutos...
    python -m venv "%PASTA%.venv" || goto :erro
    "%PASTA%.venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    "%PASTA%.venv\Scripts\python.exe" -m pip install faster-whisper yt-dlp || goto :erro
    echo Ambiente pronto.
    echo.
)
set "PY=%PASTA%.venv\Scripts\python.exe"
rem Mantem o yt-dlp atualizado (YouTube muda com frequencia)
"%PY%" -m pip install -q --upgrade yt-dlp >nul 2>&1

rem ---------- 4. Video ----------
rem Podes arrastar um video para cima deste .bat
set "FONTE=%~1"
if "%FONTE%"=="" (
    echo Cola o LINK do video ou arrasta o FICHEIRO para esta janela e carrega Enter:
    set /p "FONTE=> "
)
set "FONTE=%FONTE:"=%"
if "%FONTE%"=="" (
    echo Nenhum video indicado.
    goto :fim
)

rem ---------- 5. Opcoes ----------
echo.
set "TOP=8"
set /p "TOP=Quantos momentos queres? [8]: "

set "IDIOMA="
set /p "IDIOMA=Idioma do video (pt, en... vazio = detetar sozinho): "

echo Nicho: 1 = warhammer  2 = gaming  3 = os dois  vazio = nenhum
set "N="
set /p "N=Escolhe: "
set "NICHO="
if "%N%"=="1" set "NICHO=warhammer"
if "%N%"=="2" set "NICHO=gaming"
if "%N%"=="3" set "NICHO=warhammer,gaming"

set "PALAVRAS="
set /p "PALAVRAS=Palavras extra separadas por virgulas (opcional): "

set "MODELO=small"
echo Qualidade da transcricao: 1 = rapida (tiny)  2 = normal (small)  3 = melhor (medium)
set "Q=2"
set /p "Q=Escolhe [2]: "
if "%Q%"=="1" set "MODELO=tiny"
if "%Q%"=="3" set "MODELO=medium"

set "CORTAR=S"
set /p "CORTAR=Exportar os clips em 9:16 com legendas? (S/N) [S]: "

for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set "DATA=%%d"
set "SAIDA=%PASTA%momentos\%DATA%"

set "ARGS=--top %TOP% --modelo %MODELO% --saida "%SAIDA%""
if not "%IDIOMA%"=="" set "ARGS=%ARGS% --idioma %IDIOMA%"
if /i "%CORTAR%"=="S" set "ARGS=%ARGS% --cortar --vertical --legendas"
if not "%NICHO%"=="" set "ARGS=%ARGS% --nicho %NICHO%"

rem ---------- 6. Correr ----------
echo.
echo A processar... (videos longos podem demorar; a primeira vez descarrega o modelo)
echo.
if "%PALAVRAS%"=="" (
    "%PY%" "%PASTA%melhores_momentos.py" "%FONTE%" %ARGS%
) else (
    "%PY%" "%PASTA%melhores_momentos.py" "%FONTE%" %ARGS% --palavras "%PALAVRAS%"
)
if errorlevel 1 goto :erro

echo.
echo Feito! A abrir a pasta com os resultados...
start "" "%SAIDA%"
if exist "%SAIDA%\momentos.md" start "" notepad "%SAIDA%\momentos.md"
goto :fim

:erro
echo.
echo [ERRO] Algo correu mal. Copia a mensagem acima e manda-ma.

:fim
echo.
pause
endlocal
