   Write-Host "Starting Development Environment..." -ForegroundColor Green

   # Start Redis in a new window
   Start-Process powershell -ArgumentList "-NoExit -File .\start_redis.ps1"

   # Wait for Redis to initialize
   Start-Sleep -Seconds 2

   # Make sure venv is activated
   if (Test-Path ".\venv\Scripts\Activate.ps1") {
       Write-Host "Activating virtual environment..." -ForegroundColor Green
       .\venv\Scripts\Activate.ps1
   }

   # Run the Daphne server
   Write-Host "Starting Daphne ASGI server..." -ForegroundColor Green
   Write-Host "Access the website at http://localhost:8000/" -ForegroundColor Cyan
   daphne -v -b 127.0.0.1 -p 8000 ecommerce.asgi:application