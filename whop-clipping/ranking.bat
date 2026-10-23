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

echo.
python "%PASTA%ranking.py" --nicho "%NICHO%" --plataformas "%PLAT%"
if errorlevel 1 (
    echo.
    echo [ERRO] Algo correu mal. Copia a mensagem acima e manda-ma.
)

:fim
echo.
pause
endlocal
