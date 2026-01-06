@echo off
echo Starting RiskSentinel AI System...

:: Start Backend
start "RiskSentinel Backend" cmd /k "cd backend && py -m uvicorn main:app --reload"

:: Start Frontend
start "RiskSentinel Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo   App running at: http://localhost:5173
echo   API running at: http://localhost:8000
echo ===================================================
pause
