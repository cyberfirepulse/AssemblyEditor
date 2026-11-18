"""Built-in help. No browser or network is needed to read it."""
TOPICS = [
('Snel starten', '''1. Installeer NASM en een 64-bits GCC-toolchain (bijvoorbeeld MSYS2 UCRT64 op Windows).
2. Open Hulpmiddelen > Instellingen hulpmiddelen. Controleer de paden en sla ze op.
3. Kies Project > Laad ingebouwd voorbeeld > 01_windows_hello.asm.
4. Kies windows_x64 als doelplatform en Bouwmenu > Bouwen (automatisch).
5. Wacht op ‘Build gereed’ in de console. Kies Bouwmenu > Uitvoeren.
Het consolevoorbeeld toont ‘Hallo vanuit Windows assembly!’. Het GUI-voorbeeld opent een eigen venster.

De meegeleverde voorbeelden zijn voor Windows x64. Voor linux_x64 heb je eigen NASM ELF64-code en een Linux-toolchain nodig; de Windows-voorbeelden werken daar niet ongewijzigd.''',
'''1. Install NASM and a 64-bit GCC toolchain (for example MSYS2 UCRT64 on Windows).
2. Open Tools > Dependency settings. Check the executable paths and save them.
3. Choose Project > Load built-in example > 01_windows_hello.asm.
4. Select windows_x64 and Make > Build (auto).
5. Wait for ‘Build completed’ in the console, then choose Make > Run.
The console example prints ‘Hallo vanuit Windows assembly!’. The GUI example opens its own window.

The bundled examples target Windows x64. linux_x64 requires your own NASM ELF64 source and a Linux toolchain; the Windows examples cannot be used unchanged.'''),
('Installatie en hulpmiddelen', '''De Windows-installer bevat de editor en Python-runtime. Je hoeft Python niet apart te installeren om de geïnstalleerde app te gebruiken.

Bouwen: NASM zet .asm om naar een objectbestand; GCC koppelt dit aan een uitvoerbaar bestand. Installeer NASM via nasm.us en GCC bijvoorbeeld via msys2.org (UCRT64 of MINGW64, 64 bit). Beide moeten bij het gekozen doelplatform passen. Een Windows-installatie van GCC is geen Linux-crosscompiler.
Disassembly: objdump, doorgaans onderdeel van dezelfde GCC-toolchain.
PE-hardening: pefile is in de installer opgenomen.
ROP/JOP: installeer het externe commando ropper en zorg dat dit in PATH staat. Voor broncodegebruik: python -m pip install -r requirements.txt.
ELF-hardening: checksec moet als extern commando beschikbaar zijn.

De editor zoekt in PATH en gebruikelijke NASM/MSYS2-mappen. Gebruik Instellingen hulpmiddelen > Bladeren wanneer de detectie niets vindt. Kies de uitvoerbestanden zelf, bijvoorbeeld nasm.exe, gcc.exe en objdump.exe; kies geen map. Controleer en sla de paden op.''',
'''The Windows installer includes the editor and Python runtime; a separate Python installation is not required to run the installed app.

Builds: NASM converts .asm source into an object file; GCC links it into an executable. Install NASM from nasm.us and GCC, for example from msys2.org (64-bit UCRT64 or MINGW64). Tools must match the target platform. Windows GCC is not a Linux cross-compiler.
Disassembly: objdump, usually included in the same GCC toolchain.
PE hardening: pefile is bundled in the installer.
ROP/JOP: install the external ropper command and put it on PATH. For source use: python -m pip install -r requirements.txt.
ELF hardening: the external checksec command is required.

The editor searches PATH and common NASM/MSYS2 folders. Use Dependency settings > Browse if detection fails. Select the actual executables, such as nasm.exe, gcc.exe and objdump.exe, rather than a directory. Check and save the paths.'''),
('Bestanden en voorbeelden', '''Bestand > Nieuw begint met lege code. Openen leest een .asm- of .s-bestand als UTF-8. Opslaan als laat je een eigen .asm-bestand kiezen.

Bij Nieuw, Openen, voorbeeld laden en Afsluiten vraagt de editor of gewijzigde code eerst opgeslagen moet worden. Ja slaat op, Nee vervangt de tekst en Annuleren houdt je document open. Ook een geannuleerd opslaan of een opslagfout houdt je code intact.

Selecteer links een voorbeeld om het leerdoel te lezen en klik op Laad geselecteerd voorbeeld om de code te openen. Importeren voegt oefenbestanden aan de lijst van de huidige sessie toe; de oorspronkelijke bestanden worden niet aangepast. Bewaar eigen code met Opslaan als. Voorbeelden worden niet automatisch omgezet naar een ander besturingssysteem.''',
'''File > New starts an empty document. Open reads .asm or .s files as UTF-8. Save as lets you choose your own .asm file.

New, Open, loading examples and Exit ask whether modified source should be saved. Yes saves it, No replaces it, and Cancel keeps the document open. Cancelling the save dialog or encountering a save error also preserves your code.

Select an example in the left panel to read its learning goal; click Load selected example to open its source. Import adds exercises to the current session without modifying the original files. Save your own code using Save as. Examples are not automatically converted between operating systems.'''),
('Bouwen en uitvoeren', '''Kies eerst het doelplatform. Bouwen (automatisch) herkent WinMain/MessageBoxA als GUI-code. Met Consoleprogramma bouwen of Vensterprogramma bouwen kun je de keuze expliciet maken.

NASM en GCC draaien achtereenvolgens op de achtergrond, met elk 30 seconden time-out. De exacte opdrachten en foutmeldingen staan in de console. Je kunt blijven typen; als de bron tijdens de build verandert, wordt het resultaat niet als actuele build geselecteerd.

Uitvoeren bouwt opnieuw als de code of het doelplatform veranderd is. Een mislukte build wist de oude uitvoerselectie. Console-uitvoer verschijnt rechts. Typ invoer in het veld onder de console en kies Verzend invoer; Demo invoer werkt alleen voor voorbeelden met vooraf ingestelde invoer. De twee meegeleverde voorbeelden hebben geen invoer nodig. Stop beëindigt het actieve consoleprogramma. Een GUI-programma sluit je in zijn eigen venster.

Object- en uitvoerbestanden worden in een tijdelijke buildmap gemaakt. Sla de .asm-bron apart op. Alleen de gekozen bron wordt gebouwd; er is geen volledig project- of afhankelijkhedenbeheer.''',
'''Select the target platform first. Build (auto) recognises WinMain/MessageBoxA as GUI code. Build console and Build GUI let you choose explicitly.

NASM and GCC run sequentially in the background, each with a 30-second timeout. The console shows exact commands and errors. You can keep typing; if source changes during a build, its result is not selected as the current build.

Run rebuilds when source or target changes. Failed builds clear the previous executable selection. Console output appears on the right. Type into the field below the console and choose Send input; Demo input only works for examples with predefined inputs. The two bundled examples require no input. Stop terminates the active console program. Close GUI programs in their own windows.

Object files and executables are created in a temporary build directory. Save .asm source separately. Only the selected source is built; full project and dependency management is not provided.'''),
('Problemen oplossen', '''NASM/GCC ontbreekt: open Instellingen hulpmiddelen, kies de juiste executable, controleer en sla op. Controleer ook of je 64-bits tools hebt gekozen.
undefined symbol / symbol not defined: controleer labels, spelfouten, global/extern-declaraties en ontbrekende functies. Lees eerst de eerste foutmelding met het bijbehorende regelnummer.
undefined reference / linkerfout: controleer externe functies en bibliotheken. De GUI-build koppelt user32 en kernel32. Voor andere bibliotheken is aanpassing van de bouwketen nodig.
Verkeerd bestandsformaat: de bron, NASM-uitvoer (win64/elf64) en GCC moeten bij hetzelfde platform passen.
Time-out: de externe opdracht is afgebroken; controleer het hulpmiddel en bouw opnieuw. De vorige uitvoer wordt niet geselecteerd.
Geen console-uitvoer: controleer of het een GUI-programma is, of het programma op invoer wacht en of de build geslaagd is.
Geen ROP-gadgets: controleer ropper/PATH en de analyse-uitvoer. Geen resultaat bewijst niet dat een binary veilig is.

Syntax controleren is een beperkte controle op onder andere ontbrekende komma’s. De assembler blijft de doorslaggevende syntaxcontrole. Regeladvies verandert de code niet automatisch. Meld bij problemen de versie, het doelplatform en de console-uitvoer.''',
'''Missing NASM/GCC: open Dependency settings, choose the correct executable, check and save it. Verify that you selected 64-bit tools.
undefined symbol / symbol not defined: check labels, spelling, global/extern declarations and missing functions. Start with the first error and its line number.
undefined reference / linker error: check external functions and libraries. GUI builds link user32 and kernel32. Other libraries require changes to the build chain.
Wrong file format: source, NASM output (win64/elf64) and GCC must target the same platform.
Timeout: the external command was stopped; check the tool and rebuild. The previous executable is not selected.
No console output: check whether it is a GUI program, whether it is waiting for input and whether the build succeeded.
No ROP gadgets: check ropper/PATH and the analysis output. No result does not prove a binary is safe.

Check syntax performs limited checks, including missing commas. The assembler remains the authoritative syntax check. Line advice does not automatically rewrite code. Include the version, target platform and console output when reporting a problem.'''),
('Disassembly en registers', '''Bouw eerst de actuele bron en kies Bouwmenu > Disassembly. objdump toont de machine-instructies van de geselecteerde binary. Dit is geen debugger: er zijn geen breakpoints, stapuitvoering of live registerwaarden.

Klik in de bron om de huidige regel rechts te zien. Syntaxhulp geeft instructievoorbeelden; Register-uitleg beschrijft enkele veelgebruikte registers. Windows x64 gebruikt doorgaans RCX en RDX voor de eerste argumenten; Linux hanteert een andere calling convention.

Vergelijk bron, disassembly en uitvoer om de werking te onderzoeken. Wijzig één onderdeel tegelijk en bouw daarna opnieuw.''',
'''Build the current source first and choose Make > Disassembly. objdump shows the machine instructions of the selected binary. This is not a debugger: breakpoints, single-stepping and live register values are not provided.

Click in the source to see the current line on the right. Syntax helper provides instruction examples; Register explanation describes common registers. Windows x64 generally uses RCX and RDX for the first arguments; Linux follows a different calling convention.

Compare source, disassembly and output to investigate behaviour. Change one element at a time and rebuild.'''),
('ROP/JOP en hardening', '''Bouw de actuele code en kies Hulpmiddelen > ROP/JOP-analyse. De analyse gebruikt pefile voor PE-hardening of checksec voor ELF, en ropper voor gadgetdetectie. De analyse loopt op de achtergrond; ropper heeft 60 seconden time-out en checksec 30 seconden.

Het resultaat toont mitigaties zoals ASLR en DEP, gadgetregels en tellingen. Filter bijvoorbeeld op pop rdi, syscall, ret of jmp. Klik op een gadget voor instructieuitleg; Kopieer adres neemt het getoonde adres over.

De didactische score is een eenvoudige telling, geen kwetsbaarheidsscore of bewijs van misbruikbaarheid. Aanwezige mitigatievlaggen zijn geen volledige beveiligingsbeoordeling. De hexweergave toont de beginbytes van de binary; hij springt NIET naar de exacte bestandspositie van de geselecteerde gadget. De volledige live ROP/JOP-workflow is nog niet end-to-end gevalideerd.

Gebruik de resultaten om te leren en te onderzoeken. Bewaar context en de ruwe tooluitvoer bij conclusies.''',
'''Build the current code and choose Tools > ROP/JOP analysis. It uses pefile for PE hardening or checksec for ELF, and ropper for gadget detection. Analysis runs in the background; ropper has a 60-second timeout and checksec 30 seconds.

Results show mitigations such as ASLR and DEP, gadget lines and counts. Filter for pop rdi, syscall, ret or jmp. Click a gadget for an instruction explanation; Copy address copies the displayed address.

The learning score is a simple count, not a vulnerability rating or proof of exploitability. Mitigation flags do not constitute a full security assessment. The hex view shows the beginning of the binary; it does NOT jump to the exact file offset of the selected gadget. The complete live ROP/JOP workflow has not yet been validated end to end.

Use results for education and investigation. Preserve context and raw tool output when drawing conclusions.'''),
('Sneltoetsen en instellingen', '''Ctrl+N: nieuw; Ctrl+O: openen; Ctrl+S: opslaan; Ctrl+Shift+S: opslaan als.
F1: deze handleiding. Standaard tekstacties zoals Ctrl+C, Ctrl+V en Ctrl+Z werken in de editor. Tab voegt vier spaties in; Enter neemt de inspringing over.

Kies Taal > Nederlands of English. De interface verandert direct zonder de bron, ongedaan-maakgeschiedenis of buildselectie te vervangen. Stop eerst een lopende taak/consoleprogramma. De voorkeur wordt per gebruiker opgeslagen. Eigen broncode, voorbeeldprogramma’s en oorspronkelijke uitvoer van NASM/GCC worden niet vertaald.

Lettertype, lettergrootte en gereedschapspaden staan bij Instellingen hulpmiddelen. Beeld biedt zoom en focuskeuze. De panelen kun je via hun scheidingsranden verslepen.
Instellingen: %APPDATA%\\AssemblyEditor\\settings.json op Windows, of de AssemblyEditor-map onder ~/.config wanneer APPDATA ontbreekt. Help > Over Assembly Editor toont versie, maker en gebruiksvoorwaarden.

Help > Controleren op updates zoekt een nieuwere reguliere GitHub-release. Downloaden gebeurt na toestemming. De installer wordt met SHA-256 gecontroleerd; bij afwijking wordt hij geweigerd. Voor starten volgt een aparte bevestiging. Sla je werk op en sluit de editor voordat je de installatie afrondt.''',
'''Ctrl+N: new; Ctrl+O: open; Ctrl+S: save; Ctrl+Shift+S: save as.
F1: this guide. Standard text actions such as Ctrl+C, Ctrl+V and Ctrl+Z work in the editor. Tab inserts four spaces; Enter preserves indentation.

Choose Language > Nederlands or English. The interface changes immediately without replacing source, undo history or build selection. Stop any running task/console program first. The preference is saved per user. Your source, example programs and original NASM/GCC output are not translated.

Font, font size and tool paths are under Dependency settings. View provides zoom and focus options. Drag panel dividers to resize panels.
Settings: %APPDATA%\\AssemblyEditor\\settings.json on Windows, or AssemblyEditor under ~/.config when APPDATA is absent. Help > About Assembly Editor shows version, author and usage terms.

Help > Check for updates checks GitHub for a newer regular release. Downloads require approval and SHA-256 verification; mismatches are rejected. Starting the installer requires a second confirmation. Save your work and close the editor before completing installation.'''),
]
