[CmdletBinding(SupportsShouldProcess)]
param()

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\pythonw.exe'
$entryPoint = Join-Path $projectRoot 'main.py'

# Check the launcher before closing the existing window.
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Python was not found at '$python'. Run uv sync in '$projectRoot' first."
}
if (-not (Test-Path -LiteralPath $entryPoint -PathType Leaf)) {
    throw "The app entry point was not found at '$entryPoint'."
}

$sessionId = (Get-Process -Id $PID).SessionId
$appWindows = @(
    Get-Process -Name wormenpracticum, python, pythonw -ErrorAction SilentlyContinue |
        Where-Object {
            $_.SessionId -eq $sessionId -and (
                $_.MainWindowTitle -eq 'Wormenpracticum' -or
                $_.MainWindowTitle -like 'Wormenpracticum - *'
            )
        }
)

if ($appWindows.Count -gt 1) {
    throw 'Multiple Wormenpracticum windows are open. Close the extra instances and try again.'
}
if (-not $PSCmdlet.ShouldProcess($entryPoint, 'Restart Wormenpracticum')) {
    return
}

if ($appWindows.Count -eq 1) {
    $windowProcess = $appWindows[0]
    if (-not $windowProcess.HasExited) {
        $closeRequested = $windowProcess.CloseMainWindow()
        if (-not $windowProcess.HasExited -and
            (-not $closeRequested -or -not $windowProcess.WaitForExit(5000))) {
            throw 'Wormenpracticum did not close. Close it from the desktop, then run the script again.'
        }
    }
}

# pythonw starts the GUI without opening a separate console.
Start-Process -FilePath $python -ArgumentList ('"{0}"' -f $entryPoint) `
    -WorkingDirectory $projectRoot -WindowStyle Normal -ErrorAction Stop
