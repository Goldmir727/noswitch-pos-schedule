@echo off
echo ===================================
echo  Instalador POS System (Windows)
echo ===================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.11+ desde python.org
    pause
    exit /b 1
)

REM Verificar si Visual C++ Build Tools esta instalado
where cl.exe >nul 2>&1
if errorlevel 1 (
    echo.
    echo AVISO: No se encontro Visual C++ Build Tools.
    echo.
    echo Opciones:
    echo   1. Instalar Docker Desktop y usar: docker compose up -d
    echo   2. Instalar VS Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo Intentando instalar paquetes con wheels pre-compilados...
    echo.
)

REM Crear entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Actualizar pip
python -m pip install --upgrade pip setuptools wheel

REM Instalar dependencias criticas primero (versiones con wheels pre-compilados)
echo.
echo Instalando paquetes criticos...
pip install --only-binary=:all: lxml==5.3.0
pip install --only-binary=:all: asyncpg==0.30.0
pip install --only-binary=:all: cryptography==44.0.0
pip install --only-binary=:all: Pillow==11.1.0

REM Instalar el resto
echo.
echo Instalando resto de dependencias...
pip install -r requirements.txt

echo.
echo ===================================
echo  Instalacion completada
echo ===================================
echo.
echo Para activar el entorno: venv\Scripts\activate.bat
echo Para iniciar la API: uvicorn app.main:app --reload
pause
