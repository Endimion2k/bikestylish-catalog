@echo off
echo 🚴‍♂️ BikeStylish API - Windows Launcher
echo ==========================================

REM Verifică dacă Python există
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nu este instalat sau nu este în PATH
    echo 📥 Descarcă Python de la: https://python.org
    pause
    exit /b 1
)

REM Verifică directorul
if not exist "data" (
    echo ❌ Directorul 'data' nu există!
    echo 💡 Asigură-te că ești în directorul bikestylish-catalog
    pause
    exit /b 1
)

echo 📦 Instalez dependențele FastAPI...
python -m pip install -r requirements_fastapi.txt

echo.
echo 🚀 Pornesc BikeStylish FastAPI Server...
echo 📚 Documentație: http://localhost:8000/docs
echo 💡 Pentru oprire: Ctrl+C
echo ==========================================

REM Pornește serverul
python quick_start.py

echo.
echo ✅ Server oprit!
pause
