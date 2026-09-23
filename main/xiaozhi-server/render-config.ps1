$base = $PSScriptRoot
$tmplBytes = [IO.File]::ReadAllBytes("$base\data\.config.yaml.tmpl")
$tmpl = [Text.Encoding]::UTF8.GetString($tmplBytes)

$apiKey = $env:SAKURA_API_KEY
$vmIp = $env:VM_IP
$pcIp = $env:PC_IP

if (-not $apiKey) { Write-Warning "SAKURA_API_KEY is not set" }
if (-not $vmIp) { Write-Warning "VM_IP is not set" }
if (-not $pcIp) { Write-Warning "PC_IP is not set" }

$out = $tmpl
if ($apiKey) { $out = $out -replace '__SAKURA_API_KEY__', $apiKey }
if ($vmIp) { $out = $out -replace '__VM_IP__', $vmIp }
if ($pcIp) { $out = $out -replace '__PC_IP__', $pcIp }

[IO.File]::WriteAllText("$base\data\.config.yaml", $out, (New-Object Text.UTF8Encoding $false))
Write-Host "config rendered"
