# run-headless.ps1
# Shared library for ~/.claude/scheduled-tasks/<task>/run.ps1 entry points.
# Wraps `claude -p` with timeout, run-log append (JSONL), and Windows-toast
# escalation when preflight FAILs or the run errors.
#
# Usage:
#   . "$PSScriptRoot\..\_lib\run-headless.ps1"
#   Invoke-HeadlessTask -TaskName 'eod-sweep-headless' `
#                       -Prompt '/preflight then /eod-sweep' `
#                       -TimeoutMinutes 25 `
#                       -DryRun:$DryRun
#
# Logs: C:\Users\bblai\.claude\run-log.jsonl (one JSONL line per run)
# Escalations: C:\Users\bblai\.claude\scheduled-tasks\_escalations\<ts>-<task>.json

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ClaudeExe       = 'C:\Users\bblai\.local\bin\claude.exe'
$script:RunLogPath      = 'C:\Users\bblai\.claude\run-log.jsonl'
$script:EscalationDir   = 'C:\Users\bblai\.claude\scheduled-tasks\_escalations'

function Write-RunLog {
    param(
        [Parameter(Mandatory)] [hashtable] $Entry
    )
    $Entry['ts']  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $json = ($Entry | ConvertTo-Json -Compress -Depth 5)
    # Atomic-ish append; OK for our single-writer cadence.
    Add-Content -Path $script:RunLogPath -Value $json -Encoding utf8
}

function Show-EscalationToast {
    param(
        [Parameter(Mandatory)] [string] $Title,
        [Parameter(Mandatory)] [string] $Message
    )
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $icon = New-Object System.Windows.Forms.NotifyIcon
        $icon.Icon            = [System.Drawing.SystemIcons]::Warning
        $icon.BalloonTipTitle = $Title
        $icon.BalloonTipText  = $Message
        $icon.Visible         = $true
        $icon.ShowBalloonTip(8000)
        Start-Sleep -Seconds 9
        $icon.Dispose()
    } catch {
        # Toast failure must never break the run-log path.
        Write-Warning "Toast failed: $($_.Exception.Message)"
    }
}

function Write-Escalation {
    param(
        [Parameter(Mandatory)] [string]    $TaskName,
        [Parameter(Mandatory)] [string]    $Reason,
        [string]                          $Stdout = '',
        [string]                          $Stderr = ''
    )
    if (-not (Test-Path $script:EscalationDir)) {
        New-Item -ItemType Directory -Path $script:EscalationDir -Force | Out-Null
    }
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmssZ')
    $file = Join-Path $script:EscalationDir "$ts-$TaskName.json"
    $body = @{
        ts        = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        task      = $TaskName
        reason    = $Reason
        stdout    = $Stdout
        stderr    = $Stderr
    } | ConvertTo-Json -Depth 5
    Set-Content -Path $file -Value $body -Encoding utf8
    return $file
}

function Invoke-HeadlessTask {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TaskName,
        [Parameter(Mandatory)] [string] $Prompt,
        [int]                  $TimeoutMinutes = 20,
        [switch]               $DryRun
    )

    $start = Get-Date

    # Pre-flight the runner itself: claude.exe must exist.
    if (-not (Test-Path $script:ClaudeExe)) {
        $msg = "claude.exe not found at $script:ClaudeExe"
        Write-RunLog -Entry @{
            task          = $TaskName
            exit          = -1
            duration_s    = 0
            preflight     = 'NA'
            escalated     = $true
            error         = $msg
        }
        Show-EscalationToast -Title "Claude task: $TaskName" -Message $msg
        Write-Escalation -TaskName $TaskName -Reason $msg | Out-Null
        return @{ exit = -1; preflight = 'NA'; escalated = $true }
    }

    if ($DryRun) {
        Write-Host "[DRY RUN] Would invoke: $script:ClaudeExe -p `"$Prompt`""
        Write-RunLog -Entry @{
            task          = $TaskName
            exit          = 0
            duration_s    = 0
            preflight     = 'DRYRUN'
            escalated     = $false
            dry_run       = $true
            prompt        = $Prompt
        }
        return @{ exit = 0; preflight = 'DRYRUN'; escalated = $false }
    }

    # Run claude -p with timeout. Capture stdout/stderr to temp files so we
    # don't lose them on a hang.
    $tmpOut = [System.IO.Path]::GetTempFileName()
    $tmpErr = [System.IO.Path]::GetTempFileName()
    $exitCode = -1
    $stdout   = ''
    $stderr   = ''

    try {
        $proc = Start-Process -FilePath $script:ClaudeExe `
                              -ArgumentList @('-p', $Prompt) `
                              -RedirectStandardOutput $tmpOut `
                              -RedirectStandardError  $tmpErr `
                              -NoNewWindow -PassThru
        if (-not $proc.WaitForExit($TimeoutMinutes * 60 * 1000)) {
            try { $proc.Kill($true) } catch {}
            $exitCode = -2
            $stderr   = "Timeout after $TimeoutMinutes min"
        } else {
            $exitCode = $proc.ExitCode
        }
        if (Test-Path $tmpOut) { $stdout = Get-Content -Path $tmpOut -Raw -ErrorAction SilentlyContinue }
        if (Test-Path $tmpErr) { $stderr = ((Get-Content -Path $tmpErr -Raw -ErrorAction SilentlyContinue) + $stderr) }
    } finally {
        Remove-Item -Path $tmpOut, $tmpErr -ErrorAction SilentlyContinue -Force
    }

    $duration = [int]((Get-Date) - $start).TotalSeconds

    # Parse preflight verdict from stdout. The preflight skill emits a line
    # like "Status: GO" or "Status: BLOCKED". Also detect explicit FAIL on
    # Notion MCP / section-9 freshness.
    # NB: regex avoids the section sign (U+00A7) so PowerShell 5.1's default
    # ANSI read of this file doesn't corrupt the literal.
    $preflight = 'UNKNOWN'
    if ($stdout -match 'Status:\s*GO\b')                            { $preflight = 'PASS' }
    elseif ($stdout -match 'Status:\s*BLOCKED\b')                   { $preflight = 'FAIL' }
    elseif ($stdout -match 'Notion MCP:\s*FAIL')                    { $preflight = 'FAIL' }
    elseif ($stdout -match '9\s*freshness:\s*FAIL')                 { $preflight = 'FAIL' }
    elseif ($stdout -match '9\s*freshness:\s*WARN')                 { $preflight = 'WARN' }

    $escalated = $false
    $reason    = ''
    if ($exitCode -ne 0) {
        $escalated = $true
        $reason    = "Exit $exitCode"
    } elseif ($preflight -eq 'FAIL') {
        $escalated = $true
        $reason    = 'Preflight FAIL'
    }

    Write-RunLog -Entry @{
        task          = $TaskName
        exit          = $exitCode
        duration_s    = $duration
        preflight     = $preflight
        escalated     = $escalated
        prompt        = $Prompt
    }

    if ($escalated) {
        Show-EscalationToast -Title "Claude task: $TaskName" `
                             -Message "$reason - see run-log.jsonl"
        Write-Escalation -TaskName $TaskName `
                        -Reason   $reason `
                        -Stdout   $stdout `
                        -Stderr   $stderr | Out-Null
    }

    return @{
        exit        = $exitCode
        preflight   = $preflight
        escalated   = $escalated
        duration_s  = $duration
    }
}
