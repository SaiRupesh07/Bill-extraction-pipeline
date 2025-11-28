@echo off
echo ========================================
echo    Bill Extraction Pipeline Setup
echo ========================================
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Step 2: Creating/Activating Virtual Environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Step 3: Installing packages...
pip install fastapi uvicorn python-dotenv requests pillow numpy pydantic opencv-python-headless

echo.
echo Step 4: Creating necessary directories...
mkdir logs 2>nul
mkdir data 2>nul

echo.
echo Step 5: Testing installation...
python -c "import fastapi, uvicorn; print('✅ All packages installed successfully!')"

echo.
echo Step 6: Starting the server...
echo Press Ctrl+C to stop the server
python working_main.py

pause
