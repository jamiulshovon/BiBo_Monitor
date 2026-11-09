# remove_scheduler.ps1 - Removes BiBoTracker tasks from Windows Task Scheduler

$tasks = @(
    "BiBoTracker_0610AM", "BiBoTracker_0820AM", "BiBoTracker_1255PM", "BiBoTracker_0200PM",
    "BiBoTracker_0540AM", "BiBoTracker_06AM", "BiBoTracker_0940AM", "BiBoTracker_10AM", "BiBoTracker_0130PM", "BiBoTracker_02PM"
)

Write-Host "Removing BiBoTracker scheduled tasks..." -ForegroundColor Cyan

foreach ($task in $tasks) {
    try {
        Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction Stop
        Write-Host "[REMOVED] $task" -ForegroundColor Green
    }
    catch {
        Write-Host "[NOT FOUND] $task" -ForegroundColor DarkGray
    }
}

Write-Host "Cleanup completed." -ForegroundColor Cyan
