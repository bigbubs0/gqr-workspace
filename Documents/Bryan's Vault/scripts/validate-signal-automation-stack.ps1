$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$checks = @()

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )

    $script:checks += [pscustomobject]@{
        Name = $Name
        Status = if ($Passed) { "PASS" } else { "FAIL" }
        Details = $Details
    }
}

function Load-Json {
    param([string]$Path)
    return Get-Content -Path $Path -Raw | ConvertFrom-Json
}

$requiredFiles = @(
    "config/notion-databases.json",
    "config/signal-automations.json",
    "config/signal-health-manifest.json",
    "review/weekly-signal-automation-audit-template.md",
    "docs/plans/2026-03-07-signal-intelligence-starter-stack.md"
)

foreach ($relativePath in $requiredFiles) {
    $fullPath = Join-Path $root $relativePath
    Add-Check -Name "File exists: $relativePath" -Passed (Test-Path $fullPath) -Details $fullPath
}

$requiredDirs = @(
    "review/signals/daily",
    "review/signals/urgent",
    "review/signals/opportunities",
    "review/signals/weekly",
    "review/signals/catalysts/weekly"
)

foreach ($relativePath in $requiredDirs) {
    $fullPath = Join-Path $root $relativePath
    Add-Check -Name "Directory exists: $relativePath" -Passed (Test-Path $fullPath) -Details $fullPath
}

$notionConfigPath = Join-Path $root "config/notion-databases.json"
if (Test-Path $notionConfigPath) {
    $notionConfig = Load-Json -Path $notionConfigPath
    $dbNames = @($notionConfig.databases.PSObject.Properties.Name)
    $requiredDatabases = @(
        "company_core",
        "funding_5_50m",
        "funding_megaround",
        "layoffs",
        "positive_data",
        "active_searches",
        "candidates",
        "catalyst_calendar",
        "job_alerts"
    )

    foreach ($dbName in $requiredDatabases) {
        Add-Check `
            -Name "Notion source mapped: $dbName" `
            -Passed ($dbNames -contains $dbName) `
            -Details "Mapped sources: $($dbNames -join ', ')"
    }

    if ($dbNames -contains "job_alerts") {
        $jobAlerts = $notionConfig.databases.job_alerts
        $jobAlertsStateOk = @("pending_verification", "verified_from_local_docs", "verified") -contains $jobAlerts.status
        Add-Check `
            -Name "Job Alerts state is explicit" `
            -Passed $jobAlertsStateOk `
            -Details "Current state: $($jobAlerts.status)"
    }
}

$registryPath = Join-Path $root "config/signal-automations.json"
if (Test-Path $registryPath) {
    $registry = Load-Json -Path $registryPath
    $automationNames = @($registry.automations | ForEach-Object { $_.name })
    $requiredAutomations = @(
        "Morning Signal Radar",
        "Urgent Account Alert",
        "Opportunity Matcher",
        "Monday Market Board",
        "Monday Catalyst Board"
    )

    Add-Check `
        -Name "Five signal automations registered" `
        -Passed ($registry.automations.Count -eq 5) `
        -Details ($automationNames -join ", ")

    foreach ($name in $requiredAutomations) {
        Add-Check `
            -Name "Automation registered: $name" `
            -Passed ($automationNames -contains $name) `
            -Details ($automationNames -join ", ")
    }
}

$manifestPath = Join-Path $root "config/signal-health-manifest.json"
if (Test-Path $manifestPath) {
    $manifest = Load-Json -Path $manifestPath
    $services = @($manifest.services | ForEach-Object { $_.name })
    Add-Check `
        -Name "Signal health manifest covers five services" `
        -Passed ($manifest.services.Count -eq 5) `
        -Details ($services -join ", ")
}

$templateFiles = @(
    "review/signals/daily/_template-morning-signal-radar.md",
    "review/signals/urgent/_template-urgent-account-alert.md",
    "review/signals/opportunities/_template-opportunity-matcher.md",
    "review/signals/weekly/_template-monday-market-board.md",
    "review/signals/catalysts/weekly/_template-monday-catalyst-board.md"
)

foreach ($relativePath in $templateFiles) {
    $fullPath = Join-Path $root $relativePath
    Add-Check -Name "Template exists: $relativePath" -Passed (Test-Path $fullPath) -Details $fullPath
}

$failedChecks = @($checks | Where-Object { $_.Status -eq "FAIL" })

Write-Output "Signal Automation Stack Validation"
Write-Output ""

foreach ($check in $checks) {
    Write-Output ("[{0}] {1} - {2}" -f $check.Status, $check.Name, $check.Details)
}

Write-Output ""
Write-Output ("Summary: {0} passed, {1} failed" -f (@($checks | Where-Object { $_.Status -eq "PASS" }).Count), $failedChecks.Count)

if ($failedChecks.Count -gt 0) {
    exit 1
}
