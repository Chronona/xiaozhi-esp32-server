$base = "E:\github\stackchan-sakura\xiaozhi-esp32-server\main\xiaozhi-server"
$tmplBytes = [IO.File]::ReadAllBytes("$base\data\.config.yaml.tmpl")
$tmpl = [Text.Encoding]::UTF8.GetString($tmplBytes)
$out  = $tmpl -replace '__SAKURA_API_KEY__', $env:SAKURA_API_KEY
[IO.File]::WriteAllText("$base\data\.config.yaml", $out, (New-Object Text.UTF8Encoding $false))
Write-Host "config rendered"
