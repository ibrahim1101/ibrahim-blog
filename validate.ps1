$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
& .\.venv\Scripts\python.exe tests.py
if ($LASTEXITCODE -ne 0) { throw 'Editorial regression tests failed' }
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Workflow/security tests failed' }
npm --prefix website test
if ($LASTEXITCODE -ne 0) { throw 'Contact tests failed' }
& .\.venv\Scripts\python.exe scripts\test_fixture.py
if ($LASTEXITCODE -ne 0) { throw 'Website fixture build failed' }
Write-Host 'Offline validation passed. Live services and device-specific behavior are not tested.'
