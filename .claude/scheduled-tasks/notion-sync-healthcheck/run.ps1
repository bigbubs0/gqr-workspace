# notion-sync-healthcheck\run.ps1
# Entry point for the daily 8 AM ET Notion MCP + section9 freshness check.
# Invoked by Windows Task Scheduler.
[CmdletBinding()]
param(
    [switch] $DryRun
)

$ErrorActionPreference = 'Stop'
$libPath = Join-Path $PSScriptRoot '..\_lib\run-headless.ps1'
. $libPath

$prompt = @'
Run the preflight skill against the eod-sweep target. Output ONLY the standard
PREFLIGHT block. Do not invoke any other skill. Do not propose follow-up work.
Just the preflight result, then HALT.
'@

$result = Invoke-HeadlessTask -TaskName 'notion-sync-healthcheck' `
                              -Prompt $prompt `
                              -TimeoutMinutes 5 `
                              -DryRun:$DryRun

exit $result.exit
