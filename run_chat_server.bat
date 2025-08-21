@echo off
echo Starting Chat Server...
echo -------------------------

REM Start Redis in a separate window
start cmd /k "title Redis Server && start_redis.bat"

REM Wait for Redis to initialize
timeout /t 2 /nobreak

REM Start Django with Daphne (ASGI server)
echo Starting Django with Daphne (ASGI server)
echo Access the website at http://localhost:8000/
echo To stop the server, press Ctrl+C

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the Daphne server
daphne ecommerce.asgi:application

echo Server stopped
pause 