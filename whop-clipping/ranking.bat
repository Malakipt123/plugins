@echo off
setlocal EnableExtensions
chcp 65001 >nul
set PYTHONUTF8=1
set "PASTA=%~dp0"
cd /d "%PASTA%"
title Ranking de Campanhas - Whop

echo ============================================
echo   RANKING DE CAMPANHAS + GANHOS
echo ============================================
echo.

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [!] Python nao encontrado. Corre primeiro o melhores_momentos.bat
    echo     ou instala com: winget install -e --id Python.Python.3.12
    goto :fim
)

set "NICHO=gaming"
set /p "NICHO=Nicho a destacar [gaming]: "

set "PLAT="
set /p "PLAT=Onde publicas? (ex.: tiktok,instagram,youtube - vazio = todas): "

set "VIEWS="
set /p "VIEWS=Views esperadas por clip (vazio = a tua media): "

echo.
python "%PASTA%ranking.py" --nicho "%NICHO%" --plataformas "%PLAT%" --views "%VIEWS%"
if errorlevel 1 (
    echo.
    echo [ERRO] Algo correu mal. Copia a mensagem acima e manda-ma.
)

echo.
set "ABRIR=S"
set /p "ABRIR=Abrir os CSV no Bloco de Notas para colar dados novos? (S/N) [S]: "
if /i "%ABRIR%"=="S" (
    start "" notepad "%PASTA%campanhas.csv"
    start "" notepad "%PASTA%submissoes.csv"
)

:fim
echo.
pause
endlocal
