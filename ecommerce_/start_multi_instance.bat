@echo off
echo Starting Multi-Instance E-commerce Project...
echo =======================================

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

:: Start multiple instances of the application
echo Starting multiple Django instances with Daphne...
echo Access the website through NGINX at http://localhost/ 
echo (NGINX must be installed and configured correctly)
echo.
echo Press Ctrl+C in the respective window to stop each server

:: Start instance 1 on port 8000
start "Django Instance 1" cmd /k "call venv\Scripts\activate && daphne -b 127.0.0.1 -p 8000 ecommerce.asgi:application"

:: Wait a few seconds
timeout /t 2 /nobreak > nul

:: Start instance 2 on port 8001
start "Django Instance 2" cmd /k "call venv\Scripts\activate && daphne -b 127.0.0.1 -p 8001 ecommerce.asgi:application"

:: Wait a few seconds
timeout /t 2 /nobreak > nul

:: Start instance 3 on port 8002
start "Django Instance 3" cmd /k "call venv\Scripts\activate && daphne -b 127.0.0.1 -p 8002 ecommerce.asgi:application"

echo.
echo All instances are running.
echo Remember to have NGINX running to use the load balancer.
echo.
pause 