@echo off
echo Starting E-commerce Project...
echo ===================================

:: Activate virtual environment
call venv\Scripts\activate

:: Check if Redis is running
echo Checking Redis status...
redis-cli ping > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Redis is not running. Starting Redis...
    start "" redis-server
    echo Waiting for Redis to initialize...
    timeout /t 3 /nobreak > nul
) else (
    echo Redis is already running.
)

:: Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

:: Run the ASGI server
echo Starting Django with Daphne...
echo Access the website at http://127.0.0.1:8000/
echo Admin interface at http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server

daphne -b 127.0.0.1 -p 8000 ecommerce.asgi:application 