@echo off
echo Starting Redis server for WebSockets...
echo You may need to download Redis for Windows from https://github.com/microsoftarchive/redis/releases
echo ---------------------------------------------------------------------------------

IF EXIST "%ProgramFiles%\Redis\redis-server.exe" (
    "%ProgramFiles%\Redis\redis-server.exe"
) ELSE IF EXIST "%ProgramFiles(x86)%\Redis\redis-server.exe" (
    "%ProgramFiles(x86)%\Redis\redis-server.exe"
) ELSE (
    echo Redis server not found in standard locations.
    echo You need to install Redis to use WebSockets.
    echo Download from: https://github.com/microsoftarchive/redis/releases
    pause
) 