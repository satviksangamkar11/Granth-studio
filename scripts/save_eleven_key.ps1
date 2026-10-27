# Run this YOURSELF in your own PowerShell window (not through Claude). It asks for the ElevenLabs key with hidden typing and saves it to the secrets folder.
$dir = "D:\aai work\secrets\elevenlabs"
New-Item -ItemType Directory -Force $dir | Out-Null
$sec = Read-Host "Paste the ElevenLabs API key (hidden)" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)).Trim()
if ($key.Length -lt 16) { Write-Host "That does not look like a key. Nothing saved."; exit 1 }
Set-Content -Path "$dir\key.txt" -Value $key -NoNewline
Write-Host "Saved to $dir\key.txt (length $($key.Length)). You can close this window."
