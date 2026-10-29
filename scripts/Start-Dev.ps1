$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskRuntime = Join-Path $taskRoot '.runtime'
$taskStatePath = Join-Path $taskRuntime 'processes.json'
$taskBackend = Join-Path $taskRoot 'backend'
$taskFrontend = Join-Path $taskRoot 'frontend'
$taskPython = Join-Path $taskBackend '.venv\Scripts\python.exe'
$taskVite = Join-Path $taskFrontend 'node_modules\vite\bin\vite.js'
$taskNode = (Get-Command node -ErrorAction Stop).Source

function Test-LocalPort([int]$taskPort) {
    $taskClient = [Net.Sockets.TcpClient]::new()
    try { $taskClient.Connect('127.0.0.1', $taskPort); return $true }
    catch { return $false }
    finally { $taskClient.Dispose() }
}

function Test-BackendHealth {
    try { return (Invoke-RestMethod -Uri 'http://127.0.0.1:8100/api/v1/health' -TimeoutSec 2).status -eq 'healthy' }
    catch { return $false }
}

foreach ($taskPort in @(8100, 5310)) {
    if (Test-LocalPort $taskPort) { throw "Port $taskPort is occupied. Existing services were left running." }
}
foreach ($taskRequiredFile in @($taskPython, $taskVite)) {
    if (-not (Test-Path -LiteralPath $taskRequiredFile)) {
        throw 'Dependencies are missing. Complete the README installation steps first.'
    }
}

New-Item -ItemType Directory -Force -Path $taskRuntime | Out-Null
$taskProcesses = @()
$taskBackendProcess = Start-Process -FilePath $taskPython -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8100' -WorkingDirectory $taskBackend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRuntime 'backend.log') -RedirectStandardError (Join-Path $taskRuntime 'backend-error.log') -PassThru
$taskProcesses += @{id=$taskBackendProcess.Id;exe=$taskPython;token='app.main:app'}
@{processes=$taskProcesses} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
$taskReady = $false
for ($taskAttempt=0; $taskAttempt -lt 45; $taskAttempt++) {
    if (Test-BackendHealth) { $taskReady=$true; break }
    if ($taskBackendProcess.HasExited) { break }
    Start-Sleep -Seconds 1
}
if (-not $taskReady) { throw "Backend failed to start. Read $taskRuntime\backend-error.log and run Stop-Dev.ps1 before retrying." }

$taskFrontendProcess = Start-Process -FilePath $taskNode -ArgumentList ('"' + $taskVite + '"'), '--host', '127.0.0.1', '--port', '5310', '--strictPort' -WorkingDirectory $taskFrontend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRuntime 'frontend.log') -RedirectStandardError (Join-Path $taskRuntime 'frontend-error.log') -PassThru
$taskProcesses += @{id=$taskFrontendProcess.Id;exe=$taskNode;token=$taskVite}
@{processes=$taskProcesses} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
for ($taskAttempt=0; $taskAttempt -lt 30; $taskAttempt++) {
    try {
        $taskResponse = Invoke-WebRequest -Uri 'http://127.0.0.1:5310' -TimeoutSec 2 -UseBasicParsing
        if ($taskResponse.StatusCode -eq 200) { Write-Host 'Ready: http://127.0.0.1:5310 | API docs: http://127.0.0.1:8100/docs'; exit 0 }
    } catch {}
    if ($taskFrontendProcess.HasExited) { break }
    Start-Sleep -Seconds 1
}
throw "Frontend failed to start. Read $taskRuntime\frontend-error.log and run Stop-Dev.ps1 before retrying."
