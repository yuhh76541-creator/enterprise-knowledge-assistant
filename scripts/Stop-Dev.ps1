$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskStatePath = Join-Path $taskRoot '.runtime\processes.json'
if (-not (Test-Path -LiteralPath $taskStatePath)) { Write-Host 'No project process record found.'; exit 0 }
$taskState = Get-Content -LiteralPath $taskStatePath -Raw | ConvertFrom-Json
foreach ($taskEntry in $taskState.processes) {
    $taskProcess = Get-CimInstance Win32_Process -Filter ('ProcessId=' + [int]$taskEntry.id)
    if (-not $taskProcess) { continue }
    if (($taskProcess.ExecutablePath -ne $taskEntry.exe) -or (-not $taskProcess.CommandLine.Contains($taskEntry.token))) {
        throw "Process identity changed for PID $($taskEntry.id). It was left running."
    }
    & "$env:SystemRoot\System32\taskkill.exe" /PID $taskEntry.id /T /F | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not stop project process tree $($taskEntry.id)." }
}
Remove-Item -LiteralPath $taskStatePath
Write-Host 'Project stopped. Local knowledge data was kept.'
