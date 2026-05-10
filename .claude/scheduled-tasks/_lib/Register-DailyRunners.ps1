# Register-DailyRunners.ps1
# One-time installer (idempotent via -Force) for the headless scheduled-task
# entries. Uses the ScheduledTasks PowerShell module - wraps the Windows
# Schedule.Service COM API and avoids schtasks.exe dash-parsing failures, per
# program.md section7 "Windows Automation Preferences".
#
# Mirrors the proven pattern from C:\Users\bblai\Scripts\Register-OneDriveSortTask.ps1.
#
# Usage:
#   pwsh -File C:\Users\bblai\.claude\scheduled-tasks\_lib\Register-DailyRunners.ps1
#
# To uninstall:
#   Unregister-ScheduledTask -TaskName 'eod-sweep-headless' -Confirm:$false
#   Unregister-ScheduledTask -TaskName 'notion-sync-healthcheck' -Confirm:$false

[CmdletBinding()]
param(
    [switch] $WhatIf
)

$ErrorActionPreference = 'Stop'

$weekdays = 'Monday','Tuesday','Wednesday','Thursday','Friday'
$user     = "$env:USERDOMAIN\$env:USERNAME"

$tasks = @(
    @{
        Name        = 'eod-sweep-headless'
        Script      = 'C:\Users\bblai\.claude\scheduled-tasks\eod-sweep-headless\run.ps1'
        At          = '6:00pm'
        Description = 'Daily M-F 6 PM ET: headless EOD pipeline sweep (preflight + eod-sweep, stops at Stage 3 for Bryan review).'
        TimeLimit   = (New-TimeSpan -Minutes 30)
    },
    @{
        Name        = 'notion-sync-healthcheck'
        Script      = 'C:\Users\bblai\.claude\scheduled-tasks\notion-sync-healthcheck\run.ps1'
        At          = '8:00am'
        Description = 'Daily M-F 8 AM ET: preflight check on Notion MCP + program.md section9 freshness. Toast escalation on FAIL.'
        TimeLimit   = (New-TimeSpan -Minutes 10)
    }
)

foreach ($t in $tasks) {
    Write-Host "Registering: $($t.Name) at $($t.At) (M-F)"

    if (-not (Test-Path $t.Script)) {
        Write-Warning "  Script missing: $($t.Script) - skipping"
        continue
    }

    $action = New-ScheduledTaskAction `
        -Execute 'powershell.exe' `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$($t.Script)`""

    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $weekdays -At $t.At

    $settings = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -DontStopOnIdleEnd `
        -RestartCount 1 `
        -RestartInterval (New-TimeSpan -Minutes 10) `
        -ExecutionTimeLimit $t.TimeLimit

    $principal = New-ScheduledTaskPrincipal `
        -UserId    $user `
        -LogonType Interactive `
        -RunLevel  Limited

    if ($WhatIf) {
        Write-Host "  [WhatIf] Would Register-ScheduledTask -TaskName '$($t.Name)'"
        continue
    }

    Register-ScheduledTask `
        -TaskName    $t.Name `
        -Action      $action `
        -Trigger     $trigger `
        -Settings    $settings `
        -Principal   $principal `
        -Description $t.Description `
        -Force | Out-Null

    Write-Host "  OK"
}

Write-Host ""
Write-Host "Registered tasks:"
Get-ScheduledTask -TaskName 'eod-sweep-headless','notion-sync-healthcheck' -ErrorAction SilentlyContinue |
    Select-Object TaskName, State, @{ N='NextRun'; E={ ($_ | Get-ScheduledTaskInfo).NextRunTime } } |
    Format-Table -AutoSize
