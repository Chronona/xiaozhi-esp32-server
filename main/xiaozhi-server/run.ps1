# xiaozhi-esp32-server 起動ラッパー（uv 版・Docker 不使用）
#
# 罠1: opuslib_next は libopus を ctypes で探す。DLL を PATH に足す必要がある。
# 罠2: Python の標準出力が既定で cp932 になり、loguru が中国語ログを書けず
#      UnicodeEncodeError を延々と吐く。ログが読めなくなり、
#      レイテンシ計測（语音识别耗时: X.XXXs 等）が拾えなくなるので UTF-8 を強制する。

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$env:PATH = "$repoRoot\tools\opus;$env:PATH"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Set-Location $PSScriptRoot
& ".\.venv\Scripts\python.exe" app.py
