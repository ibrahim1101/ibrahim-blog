param([string]$TaskName = 'IbrahimBlog Draft Scheduler', [string]$DailyTime = '10:15')
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $ProjectRoot '.venv\Scripts\python.exe'))) { throw 'Run setup.ps1 first.' }
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) { throw "Task '$TaskName' already exists. Inspect it before changing it." }
$RunScript = Join-Path $PSScriptRoot 'run-scheduler.ps1'
$Action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $RunScript) -WorkingDirectory $ProjectRoot
$Triggers = @((New-ScheduledTaskTrigger -Daily -At $DailyTime), (New-ScheduledTaskTrigger -AtLogOn))
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 3) -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Principal $Principal -Settings $Settings | Out-Null
Write-Host "Installed '$TaskName'. It prepares drafts only, does not wake the PC, and runs while your user is logged in."
