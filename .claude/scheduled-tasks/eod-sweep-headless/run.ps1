# eod-sweep-headless\run.ps1
# Entry point for the daily M-F 6 PM ET headless EOD sweep.
# Invoked by Windows Task Scheduler; not by Claude directly.
[CmdletBinding()]
param(
    [switch] $DryRun
)

$ErrorActionPreference = 'Stop'
$libPath = Join-Path $PSScriptRoot '..\_lib\run-headless.ps1'
. $libPath

$prompt = @'
Run the preflight skill, then the eod-sweep skill. Stop at Stage 3 of eod-sweep
(snapshot ready for Bryan's review). Do NOT proceed to Stage 4 (Notion writeback
or draft emails) - Bryan confirms those interactively.

Output the standard preflight block, then the Stage 3 snapshot, then HALT.
'@

$result = Invoke-HeadlessTask -TaskName 'eod-sweep-headless' `
                              -Prompt $prompt `
                              -TimeoutMinutes 25 `
                              -DryRun:$DryRun

# Surface result for Task Scheduler last-run / interactive runs
exit $result.exit
