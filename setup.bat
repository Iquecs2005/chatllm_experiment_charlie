@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "PYTHON_CMD="
if exist "C:\Miniforge\python.exe" (
  set "PYTHON_CMD=C:\Miniforge\python.exe"
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -c "import sys; exit(0) if sys.version_info >= (3,10) else exit(1)"
    if !errorlevel!==0 set "PYTHON_CMD=py -3"
  )
)
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PYTHON_CMD=python"
  )
)
if not defined PYTHON_CMD (
  echo Python 3.10+ nao encontrado. Instale Python 3.10+ e tente novamente.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Criando ambiente virtual em .venv
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 exit /b 1
)

echo Atualizando pip no .venv
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo Instalando dependencias do backend
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt --no-cache-dir
if errorlevel 1 exit /b 1

if not exist ".env" (  
    echo Copie o arquivo .env enviado por e-mail para a raiz do projeto    
  )

if /I "%~1"=="run" (
  ".venv\Scripts\python.exe" -m uvicorn backend.main:app --reload
  exit /b %errorlevel%
)

echo Setup concluido.
echo Para ativar o ambiente: .venv\Scripts\activate
echo Para rodar a API: .venv\Scripts\python.exe -m uvicorn backend.main:app --reload

endlocal
