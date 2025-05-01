   Write-Host "Starting Redis Server..." -ForegroundColor Green

   # Try different possible Redis executable locations
   $redisPaths = @(
       "${env:ProgramFiles}\Redis\redis-server.exe",
       "${env:ProgramFiles(x86)}\Redis\redis-server.exe",
       "${env:ProgramFiles}\Memurai\redis-server.exe",
       "${env:ProgramFiles(x86)}\Memurai\redis-server.exe",
       "${env:ProgramFiles}\Redis Stack\redis-server.exe"
   )

   $redisExe = $null
   foreach ($path in $redisPaths) {
       if (Test-Path $path) {
           $redisExe = $path
           break
       }
   }

   if ($redisExe) {
       Write-Host "Found Redis at: $redisExe" -ForegroundColor Green
       Start-Process $redisExe
   } else {
       Write-Host "Redis not found. Please install Redis for Windows." -ForegroundColor Red
       Write-Host "Download from: https://redis.io/download/" -ForegroundColor Yellow
       Write-Host "Or use Memurai: https://www.memurai.com/get-memurai" -ForegroundColor Yellow
       pause
   }