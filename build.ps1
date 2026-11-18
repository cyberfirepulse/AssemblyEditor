$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python -m PyInstaller --noconfirm --clean --windowed --onedir --name AssemblyEditor --hidden-import pefile --icon assets/assembly-editor.ico --add-data 'assets;assets' assembly_editor.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' AssemblyEditor.iss
exit $LASTEXITCODE
