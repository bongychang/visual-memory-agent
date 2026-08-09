@echo off
echo =========================================
echo    VISUAL MEMORY ENGINE LAUNCHER
echo =========================================

:: 1. Check for Virtual Environment
IF NOT EXIST venv (
    echo [SETUP] No virtual environment found. Creating one now...
    python -m venv venv
    
    echo [SETUP] Activating environment...
    call venv\Scripts\activate
    
    echo [SETUP] Installing dependencies...
    pip install torch transformers pillow faiss-cpu fastapi uvicorn streamlit ollama requests
    
    echo [SETUP] Installation complete!
)

:: 2. Start the Backend API in a new visible window
echo [SYSTEM] Starting Backend API...
start "Visual Memory API Backend" cmd /k "call venv\Scripts\activate && uvicorn main:app --port 8000"

:: 3. Wait for the API to load (5 seconds)
echo [SYSTEM] Waiting for API to initialize...
timeout /t 5 /nobreak > NUL

:: 4. Start the Frontend UI in a new visible window
echo [SYSTEM] Starting Frontend UI...
start "Visual Memory UI Frontend" cmd /k "call venv\Scripts\activate && streamlit run app.py"

echo =========================================
echo    ALL SYSTEMS GO! 
echo    You can close this main window now.
echo =========================================
pause