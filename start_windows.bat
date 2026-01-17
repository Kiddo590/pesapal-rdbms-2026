@echo off
echo ========================================
echo  Pesapal RDBMS Challenge - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo 🚀 Setting up Python virtual environment...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 📊 Setting up demo database...
python scripts\setup_db.py

echo 🚀 Starting backend server...
start cmd /k "cd /d backend && venv\Scripts\activate.bat && uvicorn src.api.main:app --reload --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo 🚀 Starting frontend...
cd ..\frontend

REM Install frontend dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

start cmd /k "cd /d frontend && npm run dev"

echo.
echo ========================================
echo ✅ Setup Complete!
echo.
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 💡 Try these commands:
echo • REPL: python -m src.rdbms.repl.interactive
echo • Test: python -m pytest tests/
echo ========================================
echo.
echo Press any key to exit...
pause >nul