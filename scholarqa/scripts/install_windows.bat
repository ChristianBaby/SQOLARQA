@echo off
REM Script de instalacion automatica para Windows
REM ScholarQA - Sistema de Chat con PDFs Academicos

echo.
echo ========================================================
echo   ScholarQA - Instalacion Automatica (Windows)
echo ========================================================
echo.

REM Verificar Python
echo [1/6] Verificando Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado.
    echo.
    echo Por favor instala Python 3.9 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalacion marca "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo OK - Python encontrado
py --version

REM Crear entorno virtual
echo.
echo [2/6] Creando entorno virtual...
py -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo OK - Entorno virtual creado

REM Activar entorno virtual y actualizar pip
echo.
echo [3/6] Actualizando pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo OK - pip actualizado

REM Instalar dependencias
echo.
echo [4/6] Instalando dependencias...
echo (Esto puede tomar 5-10 minutos)
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Algunas dependencias fallaron
    echo Pero intentaremos continuar...
)
echo OK - Dependencias instaladas

REM Ejecutar setup
echo.
echo [5/6] Ejecutando configuracion inicial...
python setup.py
echo OK - Configuracion completada

REM Verificar instalacion
echo.
echo [6/6] Verificando instalacion...
python verify_setup.py

echo.
echo ========================================================
echo   Instalacion completada
echo ========================================================
echo.
echo PROXIMOS PASOS:
echo.
echo 1. Descarga un modelo LLM (ver INSTALACION.md)
echo    Recomendado: TinyLlama (1.1GB)
echo.
echo 2. Para iniciar el servidor:
echo    venv\Scripts\activate
echo    python src\app.py
echo.
echo 3. Abre tu navegador en: http://localhost:5000
echo.
pause
