# setup_scheduler.ps1 - Registers daily Windows scheduled tasks for BiBoTracker screenshot monitor

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    $pythonPath = (Get-Command python.exe).Source
}

$scriptPath = Join-Path $scriptDir "take_screenshot.py"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "BiBoTracker - Windows Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "Python: $pythonPath" -ForegroundColor DarkGray
Write-Host "Script: $scriptPath" -ForegroundColor DarkGray
Write-Host "==========================================================" -ForegroundColor Cyan

$schedules = @(
    @{ Name = "BiBoTracker_0610AM"; Time = "06:10"; Folder = "06-10_AM" },
    @{ Name = "BiBoTracker_0820AM"; Time = "08:20"; Folder = "08-20_AM" },
    @{ Name = "BiBoTracker_1255PM"; Time = "12:55"; Folder = "12-55_PM" },
    @{ Name = "BiBoTracker_0200PM"; Time = "14:00"; Folder = "02-00_PM" }
)

foreach ($item in $schedules) {
    $taskName = $item.Name
    $dailyTime = $item.Time
    $folder = $item.Folder

    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`" --folder `"$folder`"" -WorkingDirectory $scriptDir
    $trigger = New-ScheduledTaskTrigger -Daily -At $dailyTime
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun

    try {
        # Unregister if already exists
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "BiBoTracker admin active monitor screenshot ($folder)" | Out-Null
        Write-Host "[OK] Registered '$taskName' -> Daily at $dailyTime BST into folder $folder" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed to register '$taskName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nAll 4 tasks successfully created!" -ForegroundColor Green
Write-Host "Screenshots will be automatically saved to: $scriptDir\screenshots" -ForegroundColor Yellow
Write-Host "You can view these tasks in Windows 'Task Scheduler'." -ForegroundColor Cyan
