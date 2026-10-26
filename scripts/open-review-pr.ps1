param([Parameter(Mandatory=$true)][string]$Draft,[Parameter(Mandatory=$true)][string]$Title,[Parameter(Mandatory=$true)][string]$Description,[Parameter(Mandatory=$true)][ValidateSet('ai','cyber','gaming','dev')][string]$Category,[Parameter(Mandatory=$true)][string]$Date)
$ErrorActionPreference='Stop'
if ((git status --porcelain)) { throw 'Working tree must be clean. Back up or commit your existing changes first.' }
if ((git branch --show-current) -ne 'main') { throw 'Start on main. No files have been changed.' }
$branch='review/' + (Get-Date -Format 'yyyyMMdd-HHmmss')
git switch -c $branch
if ($LASTEXITCODE -ne 0) { throw 'Could not create review branch.' }
& .\.venv\Scripts\python.exe scripts\editor.py stage $Draft --title $Title --description $Description --category $Category --date $Date
if ($LASTEXITCODE -ne 0) { throw 'Staging canceled or failed; review branch remains for inspection.' }
Write-Host 'Review and edit the staged article, then run the commands in docs/EDITORIAL.md to commit and open a draft PR.'
