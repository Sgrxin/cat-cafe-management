$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$src = 'C:\baidunetdiskdownload\agent\agent\毕设\_kaiti_ref'
$out = Join-Path $src '_docx'
Get-Process -Name WINWORD, wps -ErrorAction SilentlyContinue | Stop-Process -Force
$files = Get-ChildItem -LiteralPath $src -Recurse -Filter '*.doc' | Where-Object { $_.Extension -eq '.doc' -and $_.DirectoryName -notmatch '_docx' }
foreach ($f in $files) {
  $rel = $f.FullName.Substring($src.Length + 1)
  $targetDir = Join-Path $out (Split-Path $rel -Parent)
  if (-not (Test-Path -LiteralPath $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }
  $target = Join-Path $targetDir ($f.BaseName + '.docx')
  if (Test-Path -LiteralPath $target) { Write-Output ("SKIP: " + $rel); continue }
  $word = $null
  try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($f.FullName, $false, $true)
    $doc.SaveAs2($target, 16)
    $doc.Close($false)
    Write-Output ("OK: " + $rel)
  } catch {
    Write-Output ("FAIL: " + $rel + " -> " + $_.Exception.Message.Split("`n")[0])
  } finally {
    if ($word) { try { $word.Quit() } catch {} }
    Get-Process -Name WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force
  }
}
