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
    @{ Name = "BiBoTracker_06AM"; Time = "06:00"; Tag = "06AM" },
    @{ Name = "BiBoTracker_0934AM"; Time = "09:34"; Tag = "09_34AM" },
    @{ Name = "BiBoTracker_10AM"; Time = "10:00"; Tag = "10AM" },
    @{ Name = "BiBoTracker_0130PM"; Time = "13:30"; Tag = "01_30PM" }
)

foreach ($item in $schedules) {
    $taskName = $item.Name
    $dailyTime = $item.Time
    $tag = $item.Tag

    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`" --tag `"$tag`"" -WorkingDirectory $scriptDir
    $trigger = New-ScheduledTaskTrigger -Daily -At $dailyTime
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun

    try {
        # Unregister if already exists
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "BiBoTracker admin active monitor screenshot ($tag)" | Out-Null
        Write-Host "[OK] Registered '$taskName' -> Daily at $dailyTime BST" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed to register '$taskName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nAll 3 tasks successfully created!" -ForegroundColor Green
Write-Host "Screenshots will be automatically saved to: $scriptDir\screenshots" -ForegroundColor Yellow
Write-Host "You can view these tasks in Windows 'Task Scheduler'." -ForegroundColor Cyan
