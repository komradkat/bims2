param (
    [string]$Mode = "dev",
    [int]$Port = 8001,
    [switch]$Setup = $false
)

Write-Host "BIMS2 Environment Manager" -ForegroundColor Magenta
Write-Host "----------------------------"

# 1. Check for 'uv' (Primary Prerequisite)
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: 'uv' is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://github.com/astral-sh/uv"
    exit 1
}

# 2. Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "Creating .env from .env.example..." -ForegroundColor Gray
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "Error: .env.example not found. Cannot proceed." -ForegroundColor Red
        exit 1
    }
}

# 3. Setup / Sync Dependencies
if ($Setup -or -not (Test-Path ".venv")) {
    Write-Host "Syncing dependencies and virtual environment..." -ForegroundColor Cyan
    uv sync
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    
    Write-Host "Running database migrations..." -ForegroundColor Cyan
    uv run python manage.py migrate
}

# 4. Profile Management
$ValidModes = @("dev", "prod")
if ($Mode -notin $ValidModes) {
    Write-Host "Error: Invalid mode '$Mode'. Use 'dev' or 'prod'." -ForegroundColor Red
    exit 1
}

# Clear any legacy env variable
Remove-Item Env:BIMS_ENV_FILE -ErrorAction SilentlyContinue

if ($Mode -eq "prod") {
    Write-Host "Profile: PRODUCTION TEST (Port $Port)" -ForegroundColor Cyan
    $env:BIMS_PROFILE = "production"
    $Settings = "config.settings.prod"
} else {
    Write-Host "Profile: DEVELOPMENT (Port $Port)" -ForegroundColor Green
    $env:BIMS_PROFILE = "development"
    $Settings = "config.settings.dev"
}

Write-Host "Starting server..." -ForegroundColor Gray
Write-Host "----------------------------"

# Run the server
uv run python manage.py runserver $Port --settings=$Settings
