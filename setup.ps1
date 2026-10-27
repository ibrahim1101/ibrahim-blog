$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Install Python 3.11+ and the Windows Python launcher.' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'Install Node.js 24+.' }
if (-not (Test-Path '.venv\Scripts\python.exe')) { py -3 -m venv .venv; if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' } }
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed' }
npm --prefix website ci
if ($LASTEXITCODE -ne 0) { throw 'Website dependency installation failed' }
Write-Host 'Setup complete. Run .\validate.ps1. Ollama models and external services must be configured separately.'
