# Assembly Editor

Assembly Editor 5.5.8 by CyberFirePulse. Windows x64 assembly editor with NASM/GCC builds, educational support, disassembly and optional ROP/JOP analysis.

[Download Windows installer](https://github.com/cyberfirepulse/AssemblyEditor/releases/latest) · [Releases](https://github.com/cyberfirepulse/AssemblyEditor/releases)

## English

Install the Setup executable. It includes the Python runtime and pefile. Install NASM and a 64-bit GCC toolchain separately (for example MSYS2 UCRT64). Select the executable paths under Tools > Dependency settings. objdump provides disassembly; the external ropper command provides gadget analysis; checksec provides ELF hardening checks.

Choose Language > English or Nederlands; the preference is saved per user. Press F1 for the full built-in guide: quick start, tool installation, files, builds and execution, troubleshooting, disassembly, ROP/JOP and settings. Version and licensing are under Help > About Assembly Editor.

Load 01_windows_hello.asm from Project, select windows_x64, choose Make > Build (auto), then Run. Source and original tool output are not translated. The bundled examples target Windows x64.

Help > Check for updates checks this repository for a newer regular release. Downloads require approval and are checked against the release SHA-256 file. Starting the installer requires a second confirmation. No automatic installation takes place.

For source use: Python 3.10+ with Tkinter, then python -m pip install -r requirements.txt and python assembly_editor.py. Keep all Python modules together. Run build.ps1 with PyInstaller and Inno Setup 6 installed to build the Windows installer.

Settings are stored in %APPDATA%/AssemblyEditor/settings.json (fallback: ~/.config/AssemblyEditor). New/Open/example loading/Exit protect unsaved work. Failed builds clear the previous executable selection. Background builds and analysis use timeouts.

See RELEASE_NOTES.md for validation and current limitations. Linux and complete live ROP/JOP analysis are not yet validated end to end. The gadget score is educational, not a vulnerability rating; the hex preview shows the beginning of the binary, not an exact gadget offset.

## Nederlands

Installeer het Setup-bestand. De Python-runtime en pefile zijn inbegrepen. Installeer NASM en een 64-bits GCC-toolchain afzonderlijk (bijvoorbeeld MSYS2 UCRT64). Kies de uitvoerbestanden bij Hulpmiddelen > Instellingen hulpmiddelen. objdump verzorgt disassembly, het externe commando ropper gadgetanalyse en checksec ELF-hardening.

Kies Taal > Nederlands of English; de voorkeur wordt per gebruiker onthouden. F1 opent de volledige handleiding: snel starten, installatie, bestanden, bouwen en uitvoeren, foutmeldingen, disassembly, ROP/JOP en instellingen. Versie en gebruiksvoorwaarden staan bij Help > Over Assembly Editor.

Laad 01_windows_hello.asm via Project, kies windows_x64, vervolgens Bouwmenu > Bouwen (automatisch), en Uitvoeren. Broncode en oorspronkelijke tooluitvoer worden niet vertaald. De meegeleverde voorbeelden zijn voor Windows x64.

Help > Controleren op updates zoekt een nieuwere reguliere GitHub-release. Downloaden gebeurt na toestemming en de installer wordt met SHA-256 gecontroleerd. Voor starten van de installer volgt een aparte bevestiging. Er wordt niet automatisch geïnstalleerd.

Voor broncodegebruik: Python 3.10+ met Tkinter, daarna python -m pip install -r requirements.txt en python assembly_editor.py. Houd alle Python-modules bij elkaar. Bouw de Windows-installer met build.ps1, PyInstaller en Inno Setup 6.

Instellingen staan in %APPDATA%/AssemblyEditor/settings.json (terugval: ~/.config/AssemblyEditor). Nieuw/Openen/voorbeeld laden/Afsluiten beschermen onopgeslagen werk. Mislukte builds wissen de vorige uitvoerselectie. Achtergrondtaken hebben time-outs.

Zie RELEASE_NOTES.md voor controles en beperkingen. Linux en volledige live ROP/JOP-analyse zijn nog niet end-to-end gevalideerd. De gadgetscore is didactisch; de hex-preview toont beginbytes, geen exacte gadgetoffset.

## License / gebruiksvoorwaarden

All rights reserved / alle rechten voorbehouden. Proprietary usage terms; see LICENSE.txt. Third-party components retain their own licenses.
