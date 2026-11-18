# Assembly Editor 5.5.7

Test release / testversie by CyberFirePulse. All rights reserved; see LICENSE.txt.

[Download Windows installer / Windows-installer downloaden](https://github.com/cyberfirepulse/AssemblyEditor/releases/tag/v5.5.7)

## English

Windows assembly editor with NASM/GCC builds, disassembly and optional ROP/JOP analysis. Includes save-before-replace prompts, protection against running stale builds, background builds with timeouts, automatic tool discovery, CyberFirePulse installer branding and a dedicated ASM application icon.

Install using the Setup executable. NASM and a 64-bit GCC toolchain (for example MSYS2) must be installed separately. Configure paths under Tools > Dependency settings. ROP/JOP requires the external ropper command; ELF hardening requires checksec. For source use, install Python 3.10+ with Tkinter and requirements.txt, then run assembly_editor.py.

Windows console build and execution, GUI build, save/cancel behavior and build failure handling were checked. Linux, a complete live ROP/JOP scan and installer installation have not yet been tested. This release is intended for testing and further improvement.

## Nederlands

# Assembly Editor 5.5.7

## Starten op Windows

Gebruik de Setup-installer en start Assembly Editor vanuit het Startmenu.
Voor broncodegebruik is Python 3.10 of nieuwer met Tkinter vereist.
Start met python assembly_editor.py.

## Hulpmiddelen

Bouwen vereist NASM en een 64-bits GCC-toolchain. De tool zoekt in PATH en in
gebruikelijke Windows-installatiemappen voor NASM en MSYS2 UCRT64/MINGW64.
Installeer NASM vanaf nasm.us en een passende GCC-toolchain, bijvoorbeeld MSYS2.
Kies ontbrekende of afwijkende paden via Tools > Dependency settings.
Disassembly gebruikt objdump uit dezelfde toolchain.
ROP/JOP-analyse gebruikt het commando ropper en PE-hardening gebruikt pefile.
Voor broncodegebruik: python -m pip install -r requirements.txt.
Voor een installerinstallatie moet ropper als extern commando beschikbaar zijn.
De installer bundelt pefile voor PE-hardening. ELF-hardening gebruikt checksec.

## Werkwijze

Laad een voorbeeld, bouw via Make > Build en start via Make > Run.
Wijzigingen worden gecontroleerd bij Nieuw, Openen, voorbeeld laden en Afsluiten.
Bij Ja sla je op, bij Nee vervang je de code en bij Annuleren blijf je in het document.
Run bouwt gewijzigde code opnieuw. Een mislukte build geeft geen vorige binary vrij.
Tijdens een build kun je blijven typen. Bouw opnieuw als de bron ondertussen verandert.
Build en ROP/JOP draaien op de achtergrond. NASM/GCC hebben elk 30 seconden,
checksec 30 seconden en ropper 60 seconden. Een time-out verschijnt in de console.

Instellingen staan in de gebruikersconfiguratiemap AssemblyEditor/settings.json.
De release bevat geen persoonlijke instellingen of vooraf ingevulde absolute paden.

## Bouwen van de installer

Installeer PyInstaller. Bouw met:
python -m PyInstaller --noconfirm --windowed --onedir --name AssemblyEditor --hidden-import pefile --icon assets/assembly-editor.ico --add-data "assets;assets" assembly_editor.py
Compileer daarna AssemblyEditor.iss met Inno Setup 6.
Alle vier Python-bestanden moeten in dezelfde bronmap blijven.

## Controle van deze release

Op Windows zijn documentannulering, opslaan, instellingen, een echte consolebuild
met correcte uitvoer, een GUI-build, fouten bij bouwen, achtergrondtaken en time-outs
gecontroleerd. De Linux-bouwketen en het openen van de GUI-voorbeeldbinary zijn niet
getest. De volledige ROP/JOP-uitvoer is afhankelijk van de externe tools.

## Gebruiksvoorwaarden

Eigen gebruiksvoorwaarden, alle rechten voorbehouden. Zie LICENSE.txt.

De Windows-installer gebruikt de bestaande CyberFirePulse-wizardafbeeldingen en het CyberFirePulse-setupicoon. De app en snelkoppelingen gebruiken het ASM-chipicoon. Bouw beide via build.ps1.

