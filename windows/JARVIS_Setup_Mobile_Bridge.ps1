$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$bridge = Join-Path $root "JARVIS_Mobile_Bridge.py"
$actions = Join-Path $env:USERPROFILE "OneDrive\Desktop\jarvis interface\actions.py"
$configDir = Join-Path $env:LOCALAPPDATA "JARVIS"
$configPath = Join-Path $configDir "mobile-bridge.json"
$taskName = "JARVISMobileBridge"

if (-not (Test-Path -LiteralPath $bridge)) {
    throw "JARVIS_Mobile_Bridge.py doit être dans le même dossier que ce script."
}
if (-not (Test-Path -LiteralPath $actions)) {
    $actions = Read-Host "Chemin complet vers actions.py"
}
if (-not (Test-Path -LiteralPath $actions)) {
    throw "actions.py introuvable : $actions"
}

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $pythonCommand) { throw "Python n'est pas trouvé dans PATH. Installe Python ou ajoute python.exe au PATH." }
$pythonExe = $pythonCommand.Source

New-Item -ItemType Directory -Path $configDir -Force | Out-Null
$bytes = New-Object byte[] 48
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
$token = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+','-').Replace('/','_')

$config = @{
    token = $token
    actions_path = (Resolve-Path -LiteralPath $actions).Path
    python_exe = $pythonExe
    port = 8765
}
$config | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8

schtasks.exe /Delete /TN $taskName /F 2>$null | Out-Null
$taskCommand = '"' + $pythonExe + '" "' + $bridge + '"'
schtasks.exe /Create /TN $taskName /SC ONLOGON /TR $taskCommand /F | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Impossible de créer la tâche planifiée $taskName." }

$existing = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    Start-Process -FilePath $pythonExe -ArgumentList @('"' + $bridge + '"') -WorkingDirectory $root -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Pont JARVIS installé. Tâche Windows : $taskName" -ForegroundColor Green
Write-Host "Fichier de configuration : $configPath"
Write-Host "Port local du pont : 8765"
Write-Host ""
Write-Host "CLE PRIVEE A COLLER DANS L'APPLICATION IOS :" -ForegroundColor Yellow
Write-Host $token -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT : ton tunnel Cloudflare doit pointer vers http://127.0.0.1:8765 (pas le port 5000)."
Write-Host "Pour un test Quick Tunnel, dans une autre fenêtre PowerShell, lance :"
Write-Host "cloudflared tunnel --url http://127.0.0.1:8765"
Write-Host "Puis copie l'adresse https://....trycloudflare.com dans l'application."
Write-Host ""
