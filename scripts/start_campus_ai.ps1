param([switch]$StartBackend)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$aiRoot=Join-Path $projectRoot '.tools/ai'
if(!(Test-Path -LiteralPath (Join-Path $aiRoot 'model.onnx')) -or !(Test-Path -LiteralPath (Join-Path $aiRoot 'qdrant.exe'))){throw 'Run python scripts/setup_campus_ai.py first'}
try { $null=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:6333/healthz' -TimeoutSec 2 }
catch { Start-Process (Join-Path $aiRoot 'qdrant.exe') -ArgumentList '--config-path','qdrant.yaml' -WorkingDirectory $aiRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $aiRoot 'qdrant.log') -RedirectStandardError (Join-Path $aiRoot 'qdrant-error.log') }
if($StartBackend){
 if(!$env:DB_PASSWORD){throw 'Set DB_PASSWORD before starting the backend'}
 if(!(Test-Path -LiteralPath (Join-Path $projectRoot '.env.ai'))){throw 'Create a campus-local .env.ai using .env.example'}
 $env:CAMPUS_AI_ENABLED='true'
 Start-Process java -ArgumentList '-jar','backend/target/smart-life-0.1.0-SNAPSHOT.jar' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot '.tools/backend.log') -RedirectStandardError (Join-Path $projectRoot '.tools/backend-error.log')
}
Write-Output 'Campus AI dependencies started. Qdrant binds only to 127.0.0.1:6333.'
