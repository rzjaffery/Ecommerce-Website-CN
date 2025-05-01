@echo off
echo Starting E-commerce Project with HTTPS...
echo =====================================

:: Check if certificates exist, generate if not
if not exist certificates\dev-cert.pem (
    echo SSL certificates not found. Generating...
    call create_ssl_cert.bat
)

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

:: Run the ASGI server with SSL
echo Starting Django with Daphne and SSL...
echo Access the website at https://localhost:8443/
echo Admin interface at https://localhost:8443/admin/
echo.
echo WARNING: Your browser may show a security warning because of the self-signed certificate.
echo          This is normal in development. You can safely proceed.
echo.
echo Press Ctrl+C to stop the server

daphne -e ssl:8443:privateKey=certificates\dev-key.pem:certKey=certificates\dev-cert.pem -b 0.0.0.0 ecommerce.asgi:application 