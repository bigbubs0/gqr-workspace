#!/usr/bin/env bash
# Reads JSON from stdin (canonical Claude Code hook protocol).
# Warns (does NOT block) when a Bash/PowerShell command matches a known
# elevation-required pattern. Exit 0 always — this is a heads-up so Bryan sees
# the elevation wall coming before the permission prompt fires, not a guard rail.
#
# Why warn-not-block: per program.md §7 "Windows Automation Preferences",
# Bryan wants elevation needs flagged upfront rather than discovered mid-task.
# A hard block would prevent legitimate admin work he's already prepared for.

set -euo pipefail

# Use jq.exe at the known absolute path — `jq` isn't on PATH inside bash -c
# launched by the Claude Code hook runner.
JQ='/c/Users/bblai/.claude/jq.exe'

PAYLOAD="$(cat)"
TOOL_NAME=$(echo "$PAYLOAD" | "$JQ" -r '.tool_name // ""')

case "$TOOL_NAME" in
  Bash|PowerShell)
    CMD="$(echo "$PAYLOAD" | "$JQ" -r '.tool_input.command // ""')"
    ;;
  *)
    exit 0
    ;;
esac

# Empty command -> nothing to scan
[[ -z "$CMD" ]] && exit 0

# Patterns that almost always need admin / UAC on Windows (case-insensitive).
# Keep tight — false positives erode trust in the warning.
elev_re='Set-MpPreference|MpPreference -Disable|Tamper.?Protection|Disable-WindowsOptionalFeature|Enable-WindowsOptionalFeature|Stop-Service|Start-Service|Set-Service|Uninstall-WindowsFeature|Install-WindowsFeature|takeown\b|icacls\s.*\\Windows\\|HKLM:\\|HKEY_LOCAL_MACHINE|New-ItemProperty\s+-Path\s+["'"'"']?HKLM|Set-ItemProperty\s+-Path\s+["'"'"']?HKLM|schtasks\s+/(create|change|delete)|sc\s+(create|delete|stop|start|config)\b|Disable-ScheduledTask|Enable-ScheduledTask\s+-TaskPath\s+["'"'"']?\\(Microsoft|Windows)|bcdedit\b|reg\s+(add|delete)\s+HKLM\\|netsh\s+advfirewall|wmic\s+'

if echo "$CMD" | grep -qiE "$elev_re"; then
  # Identify which pattern matched for a more helpful message.
  reason="unknown elevation pattern"
  if echo "$CMD" | grep -qiE 'Set-MpPreference|Tamper.?Protection'; then
    reason="Defender / Tamper Protection — UAC + Tamper-Protection wall"
  elif echo "$CMD" | grep -qiE 'schtasks\s+/(create|change|delete)'; then
    reason="schtasks.exe — prefer the COM API (Schedule.Service) per program.md §7. See Register-OneDriveSortTask.ps1 for the canonical pattern"
  elif echo "$CMD" | grep -qiE 'HKLM:\\|HKEY_LOCAL_MACHINE|reg\s+(add|delete)\s+HKLM'; then
    reason="HKLM registry write — needs admin; corporate GPO may also block"
  elif echo "$CMD" | grep -qiE 'Stop-Service|Start-Service|Set-Service|sc\s+(create|delete|stop|start|config)'; then
    reason="service control — needs admin"
  elif echo "$CMD" | grep -qiE 'Disable-WindowsOptionalFeature|Enable-WindowsOptionalFeature|Uninstall-WindowsFeature|Install-WindowsFeature'; then
    reason="Windows feature change — needs admin"
  elif echo "$CMD" | grep -qiE 'takeown|icacls'; then
    reason="ownership / ACL change on system path — needs admin"
  elif echo "$CMD" | grep -qiE 'bcdedit|netsh\s+advfirewall'; then
    reason="boot config / firewall change — needs admin"
  fi

  cat >&2 <<MSG
WARN (preuse-warn-elevation): this command likely needs admin / UAC.
Reason: $reason

Per program.md §7 (Windows Automation Preferences): assume non-admin context and
flag elevation needs upfront. If this is intentional and you have an elevated
shell ready, proceed. If not, either:
  1. Re-launch the terminal as admin first, or
  2. Pick a non-elevated alternative (COM over schtasks, user-scope registry, etc.)

This is a warning only — the command will still run if you approve the prompt.
MSG
fi

exit 0
