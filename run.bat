@echo off
REM Batch file to run the Syria-Gpt project
echo ============================================
echo Syria-GPT Clean Architecture API
echo ============================================
echo.

REM Handle the "stop" argument
if "%1"=="stop" (
    echo Stopping the application...
    docker-compose -f deployment/docker-compose.yml down
    if %errorlevel% equ 0 (
        echo Application stopped successfully.
    ) else (
        echo Error stopping the application.
        exit /b 1
    )
    exit /b 0
)

REM Handle the "rebuild" argument
if "%1"=="rebuild" (
    echo Rebuilding containers from scratch...
    docker-compose -f deployment/docker-compose.yml down
    docker-compose -f deployment/docker-compose.yml build --no-cache
    goto :start_containers
)

REM Handle the "logs" argument
if "%1"=="logs" (
    echo Showing application logs...
    docker-compose -f deployment/docker-compose.yml logs -f syria-gpt-app
    exit /b 0
)

REM Handle the "status" argument
if "%1"=="status" (
    echo Checking application status...
    docker-compose -f deployment/docker-compose.yml ps
    exit /b 0
)

REM Check if Docker is running
echo Checking Docker status...
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker and try again.
    exit /b 1
)
echo Docker is running.

REM Check if containers are already running
docker ps -f "name=syria-gpt-app" -f "status=running" | find "syria-gpt-app" >nul
if %errorlevel% equ 0 (
    docker ps -f "name=syria-gpt-db" -f "status=running" | find "syria-gpt-db" >nul
    if %errorlevel% equ 0 (
        echo Containers are already running.
        goto :check_health
    )
)

REM Check if containers exist but are stopped
docker ps -a -f "name=syria-gpt-app" | find "syria-gpt-app" >nul
if %errorlevel% equ 0 (
    echo Starting existing containers...
    docker-compose -f deployment/docker-compose.yml start
    if %errorlevel% neq 0 (
        echo Failed to start existing containers. Rebuilding...
        goto :build_containers
    )
    goto :check_startup
)

:build_containers
echo Building and starting Docker containers...
docker-compose -f deployment/docker-compose.yml up -d --build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build or start containers.
    echo Run 'run.bat logs' to see detailed error logs.
    exit /b 1
)
goto :check_startup

:start_containers
echo Starting containers...
docker-compose -f deployment/docker-compose.yml up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers.
    echo Run 'run.bat logs' to see detailed error logs.
    exit /b 1
)

:check_startup

REM Wait for containers with progressive checks
echo Waiting for containers to be ready...
timeout /t 3 /nobreak >nul

REM Check if the containers are running
docker ps -f "name=syria-gpt-app" -f "status=running" | find "syria-gpt-app" >nul
if %errorlevel% neq 0 (
    echo Waiting a bit more for application container...
    timeout /t 5 /nobreak >nul
    docker ps -f "name=syria-gpt-app" -f "status=running" | find "syria-gpt-app" >nul
    if %errorlevel% neq 0 (
        echo ERROR: Application container failed to start.
        echo Run 'docker logs syria-gpt-app' for details.
        exit /b 1
    )
)

:check_health

REM Check database connectivity with retry logic
echo Checking database connection...
set /a retry_count=0
:db_retry
docker exec syria-gpt-db pg_isready -U admin -d syriagpt >nul 2>nul
if %errorlevel% equ 0 (
    echo Database is ready.
    goto :run_migrations
)
set /a retry_count+=1
if %retry_count% lss 6 (
    echo Database not ready yet, waiting... (attempt %retry_count%/5)
    timeout /t 2 /nobreak >nul
    goto :db_retry
)
echo ERROR: Database failed to become ready after 5 attempts.
echo Run 'docker logs syria-gpt-db' for details.
exit /b 1

:run_migrations

REM Run database migrations
echo Running database migrations...
docker exec syria-gpt-app alembic upgrade head
if %errorlevel% neq 0 (
    echo ERROR: Database migration failed.
    exit /b 1
)
echo Migrations completed successfully.

REM Health check with retry
echo Performing health check...
set /a health_retry=0
:health_retry
curl -f http://localhost:9000/health >nul 2>nul
if %errorlevel% equ 0 (
    echo Health check passed.
    goto :success
)
set /a health_retry+=1
if %health_retry% lss 4 (
    echo Health check failed, retrying... (attempt %health_retry%/3)
    timeout /t 3 /nobreak >nul
    goto :health_retry
)
echo WARNING: Health check failed after 3 attempts.
echo Application may still be starting. Try accessing http://localhost:9000/health manually.

:success

echo.
echo ============================================
echo     Syria-GPT API is now running!
echo ============================================
echo API Endpoints:
echo   - Main API: http://localhost:9000
echo   - Health Check: http://localhost:9000/health
echo   - Documentation: http://localhost:9000/docs
echo   - Admin UI: http://localhost:5050 (admin@admin.com / admin123)
echo.
echo Useful commands:
echo   run.bat           - Start application (smart mode)
echo   run.bat stop      - Stop the application
echo   run.bat rebuild   - Force rebuild containers
echo   run.bat logs      - Show application logs
echo   run.bat status    - Check container status
echo.
echo Press Ctrl+C to exit this script (containers will keep running)
echo ============================================
