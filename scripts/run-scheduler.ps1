$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Run setup.ps1 first.' }
$LogDir = Join-Path $ProjectRoot 'data\logs'
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$LogPath = Join-Path $LogDir 'scheduler.log'
"`n=== $(Get-Date -Format o) ===" | Out-File -FilePath $LogPath -Append -Encoding utf8
& $Python (Join-Path $ProjectRoot 'scripts\scheduler.py') *>&1 | Out-File -FilePath $LogPath -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
