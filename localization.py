"""Application-owned text only; source code and external tool output stay untouched."""
import re

language = 'nl'

# Each row is Dutch | English. Technical names and assembler instructions stay intact.
PAIRS = '''Bestand|File
Overig|Other
(geen data)|(no data)
Kon binary niet lezen voor hex-preview: |Could not read binary for hex preview: 
RUWE ROPPER-OUTPUT|RAW ROPPER OUTPUT
Bouwen|Build
ROP/JOP analyse|ROP/JOP analysis
Controleren op updates|Check for updates
Controleren op updates...|Checking for updates...
Ongeldige releaseversie.|Invalid release version.
Ongeldige downloadbron.|Invalid download source.
Download is groter dan toegestaan.|Download exceeds the size limit.
De release mist een installer of controlesommenbestand.|The release is missing an installer or checksum file.
Geen geldige SHA-256 voor de installer gevonden.|No valid SHA-256 was found for the installer.
SHA-256 komt niet overeen. De installer wordt niet gestart.|SHA-256 does not match. The installer will not be started.
Je gebruikt de nieuwste beschikbare versie.|You are using the latest available version.
Nieuwe versie beschikbaar: |New version available: 
Installer downloaden en met SHA-256 controleren?|Download the installer and verify its SHA-256?
Update downloaden en controleren...|Downloading and verifying update...
Download gecontroleerd. Installer starten? Sla je werk op en sluit de editor voordat je de installatie afrondt.|Download verified. Start the installer? Save your work and close the editor before completing installation.
Update installeren|Install update
Deze installer is alleen voor Windows.|This installer is for Windows only.
Leerdoel: native Windows x64 met main en printf.|Learning goal: native Windows x64 with main and printf.
Leerdoel: eerste Windows GUI voorbeeld met MessageBoxA.|Learning goal: first Windows GUI example with MessageBoxA.
Een grafisch berichtvenster.|A graphical message window.
Stackruimte voor externe call.|Stack space for an external call.
Adres van msg gaat RIP-relatief naar RCX.|The RIP-relative address of msg is passed in RCX.
RDX wijst naar de boodschap.|RDX points to the message.
R8 wijst naar de venstertitel.|R8 points to the window title.
Geen invoer nodig. Klik op Run en bekijk alleen de output.|No input is needed. Click Run to see the output.
Geen console-invoer nodig. Run opent direct een grafisch venster.|No console input is needed. Run opens a graphical window.
Bewerken|Edit
Bouwmenu|Make
Hulpmiddelen|Tools
Beeld|View
Ongedaan maken|Undo
Opnieuw uitvoeren|Redo
Nieuw|New
Openen...|Open...
Opslaan als...|Save as...
Opslaan|Save
Afsluiten|Exit
Knippen|Cut
Kopieren|Copy
Plakken|Paste
Alles selecteren|Select all
Zoeken...|Find...
Zoeken|Find
Zoekterm:|Search term:
Geen resultaten voor:|No results for:
resultaat/resultaten voor|result(s) for
Voorbeeldenvenster|Examples window
Laad ingebouwd voorbeeld|Load built-in example
Importeer oefenbestanden...|Import exercise files...
Importeer oefenbestanden|Import exercise files
Voorbeeldbestanden|Example files
Laad geselecteerd voorbeeld|Load selected example
Voorbeelden|Examples
Laad|Load
Syntax controleren|Check syntax
Bouwen (automatisch)|Build (auto)
Consoleprogramma bouwen|Build console
Vensterprogramma bouwen|Build GUI
Uitvoeren|Run
Demo uitvoeren|Run demo
Analyse en advies|Analyse + fix
Regeladvies|Fix regel
Syntaxhulp|Syntax helper
Register-uitleg|Register explanation
ROP/JOP-analyse|ROP/JOP analysis
Instellingen hulpmiddelen|Dependency settings
Instellingen|Settings
Wis console|Clear console
Toon runtime-hint|Show runtime hint
Zoom uit|Zoom out
Focus op editor|Focus editor
Focus op console|Focus console
Doelplatform:|Target:
Uitvoer / Console|Output / Console
Verzend invoer|Send input
Demo invoer|Demo input
Regel-uitleg / didactische hulp|Line explanation / learning support
Leerdoel / verwacht resultaat|Learning goal / expected result
Klaar|Ready
Regel |Line 
, kolom |, column 
Dependencies: onbekend|Dependencies: unknown
Runtime-hint: laad een voorbeeld of bouw je eigen programma.|Runtime hint: load an example or build your own program.
Geen specifieke input-hint beschikbaar.|No specific input hint available.
Typ invoer onderaan en klik op 'Verzend invoer'.|Type input at the bottom and click 'Send input'.
Categorie:|Category:
Verwachte output:|Expected output:
Didactische modus actief.|Learning mode enabled.
Klik op een regel voor uitleg.|Click a line for an explanation.
Voorbeeld geladen:|Example loaded:
Geimporteerde oefeningen|Imported exercises
Geimporteerd oefenbestand.|Imported exercise file.
Controleer comments in het bestand of voer het programma uit.|Check the comments in the file or run the program.
Controleer comments in het bestand. Typ invoer handmatig indien nodig.|Check the comments in the file. Enter input manually if needed.
Importfout voor|Import error for
oefenbestand(en) geimporteerd.|exercise file(s) imported.
Wijzigingen opslaan|Save changes
Wil je de gewijzigde code eerst opslaan?|Save the modified code first?
Openen mislukt|Open failed
Opslaan mislukt|Save failed
Assemblybestanden|Assembly files
Alle bestanden|All files
Uitvoerbare bestanden|Executable files
Instructie '|Instruction '
' verwacht meestal 2 operanden.|' usually expects 2 operands.
Geen duidelijke syntaxproblemen gevonden.|No obvious syntax problems found.
Automatische fix is in deze merge beperkt gehouden.|Automatic fixes are limited; review and correct the code manually.
Snelle syntaxhulp|Quick syntax help
GUI voorbeeld:|GUI example:
vaak ook tijdelijke werkruimte.|often also temporary workspace.
algemeen register, vaak gebruikt voor tussenresultaten.|general register, often used for intermediate results.
op Windows x64 meestal het eerste argumentregister.|usually the first argument register on Windows x64.
op Windows x64 meestal het tweede argumentregister.|usually the second argument register on Windows x64.
Wacht tot de huidige taak klaar is.|Wait until the current task finishes.
Taak mislukt:|Task failed:
Stop het programma of wacht tot de huidige taak klaar is.|Stop the program or wait until the current task finishes.
ontbreekt. Kies het uitvoerbestand via Tools > Dependency settings.|is missing. Choose its executable under Tools > Dependency settings.
Bron gewijzigd tijdens bouwen. Bouw opnieuw voor de actuele code.|Source changed during the build. Rebuild the current code.
Build gereed:|Build completed:
Er draait al een programma. Kies eerst Stop.|A program is already running. Choose Stop first.
[GUI-programma gestart]|[GUI program started]
GUI-programma's tonen meestal een apart venster en gebruiken geen console-invoer.|GUI programs usually show a separate window and do not use console input.
GUI runtime start fout:|GUI runtime start error:
Runtime start fout:|Runtime start error:
[Runtime gestart]|[Runtime started]
GUI-programma's gebruiken hier meestal geen demo-invoer.|GUI programs usually do not use demo input here.
Dit voorbeeld heeft geen demo-invoer nodig.|This example does not require demo input.
Geen actief voorbeeld geladen.|No active example loaded.
Runtime beeindigd met code|Runtime exited with code
Er draait geen consoleprogramma.|No console program is running.
[Stop aangevraagd]|[Stop requested]
objdump niet gevonden:|objdump not found:
Disassembly fout:|Disassembly error:
Bouw eerst een binary voordat je ROP/JOP analyse doet.|Build a binary before starting ROP/JOP analysis.
Bouw eerst de actuele code voor analyse.|Build the current code before analysing it.
ROP/JOP analyse - didactische modus|ROP/JOP analysis - learning mode
ROP/JOP analyse geopend.|ROP/JOP analysis opened.
Binary hardening / gadgetscan|Binary hardening / gadget scan
Resultaten en uitleg|Results & explanation
ROP gadgets (didactisch)|ROP gadgets (learning mode)
Uitleg bij geselecteerde gadget|Selected gadget explanation
Nog geen gadget/mapping geselecteerd.|No gadget/mapping selected yet.
Selecteer eerst een gadgetregel.|Select a gadget line first.
(onbekend)|(unknown)
Geselecteerde gadget:|Selected gadget:
Adres:|Address:
Didactische opmerking:|Learning note:
De exacte VA->file offset mapping is in deze versie vereenvoudigd.|Exact VA-to-file-offset mapping is simplified in this version.
Hieronder zie je een preview van de binarybeginbytes.|The preview below shows the first bytes of the binary.
Hex viewer - geselecteerde gadget|Hex viewer - selected gadget
Adres gekopieerd|Address copied
Kopieren mislukt|Copy failed
Didactische toelichting|Learning notes
RET-gadgets zijn klassiek relevant voor ROP-ketens.|RET gadgets are traditionally relevant to ROP chains.
JMP/CALL-gadgets zijn interessanter in een JOP-context.|JMP/CALL gadgets are more relevant in a JOP context.
POP->RET-gadgets helpen vaak om registers op te bouwen.|POP-to-RET gadgets often help populate registers.
Hexweergave helpt studenten de link te leggen tussen binaire bytes en gedisassembleerde instructies.|Hex views help link binary bytes to disassembled instructions.
De huidige hexweergave toont een vereenvoudigde preview; voor volledige adresmapping is een uitgebreidere offset-resolutie nodig.|The current hex view is a simplified preview; full address mapping requires more extensive offset resolution.
Meer info: gadgets & hex|More information: gadgets & hex
Scan ROP-gadgets|Show ROP gadgets
Toepassen|Apply
Open Hex bij gadget-regel|Open hex for gadget line
Open Hex (geselecteerde gadget)|Open hex (selected gadget)
Kopieer adres|Copy address
MITIGATIES|MITIGATIONS
ROP-SAMENVATTING|ROP SUMMARY
DIDACTISCHE SCORE|LEARNING SCORE
RET-gerelateerde telling:|RET-related count:
Indirecte JMP telling:|Indirect JMP count:
Indirecte CALL telling:|Indirect CALL count:
POP->RET telling:|POP-to-RET count:
Didactische totaalscore:|Total learning score:
Snelle gadgetstatistiek|Quick gadget statistics
Totaal getelde gadgetregels:|Total gadget lines counted:
JMP-gerelateerd:|JMP-related:
CALL-gerelateerd:|CALL-related:
Getoond:|Shown:
Klik op een gadgetregel hierboven om uitleg te zien.|Click a gadget line above to see an explanation.
Dubbelklik opent de hex-viewer direct.|Double-click to open the hex viewer.
Bladeren...|Browse...
Lettertype|Font family
Lettergrootte|Font size
NASM-pad|NASM path
GCC-pad|GCC path
Objdump-pad|Objdump path
Kies NASM|Choose NASM
Kies GCC|Choose GCC
Kies objdump|Choose objdump
Klik op 'Check nu', 'Browse...' of 'Auto detect'.|Click 'Check now', 'Browse...' or 'Auto detect'.
Auto detect uitgevoerd.|Auto detection completed.
Controle:|Check:
Nu controleren|Check now
Instellingen opslaan mislukt|Failed to save settings
Selecteer een gadgetregel die met 0x begint.|Select a gadget line starting with 0x.
Geen instructies gevonden.|No instructions found.
Didactische uitleg per stap:|Step-by-step learning explanation:
Laadt een waarde van de stack in een register.|Loads a value from the stack into a register.
Verplaatst data van bron naar doel.|Moves data from source to destination.
Bitwise XOR; vaak gebruikt om een register op nul te zetten.|Bitwise XOR; often used to clear a register.
Telt waarden op.|Adds values.
Trekt waarden af.|Subtracts values.
Berekent een adres zonder geheugeninhoud direct te lezen.|Calculates an address without reading its contents.
Zet een waarde op de stack.|Pushes a value onto the stack.
Keert terug via de stack; klassiek relevant voor ROP.|Returns using the stack; traditionally relevant to ROP.
Maakt een sprong; indirecte varianten zijn interessant voor JOP.|Jumps; indirect variants are relevant to JOP.
Roept een functie of doel aan; indirecte call-patronen zijn interessant.|Calls a function or target; indirect call patterns are relevant.
Algemene instructie.|General instruction.
Kon 'pefile' niet importeren. Installeer met: pip install pefile|Could not import 'pefile'. Install using: pip install pefile
fout|error
Kon PE niet lezen:|Could not read PE:
Het commando 'checksec' is niet gevonden in PATH.|The 'checksec' command was not found in PATH.
Het commando 'ropper' is niet gevonden.|The 'ropper' command was not found.
Geen output ontvangen van ropper.|No output received from ropper.
Aantal gevonden gadgets:|Number of gadgets found:
Opmerking: ropper gaf geen bruikbare gadgetregels terug.|Note: ropper did not return usable gadget lines.
Aantal gevonden gadgets (ruwe telling):|Number of gadgets found (raw count):
Voorbeeldgadgets:|Example gadgets:
Gebruikershandleiding|User guide
Over Assembly Editor|About Assembly Editor
Taal|Language
Sluiten|Close
Snel starten|Quick start
Installatie en hulpmiddelen|Installation and tools
Bestanden en voorbeelden|Files and examples
Bouwen en uitvoeren|Build and run
Problemen oplossen|Troubleshooting
Disassembly en registers|Disassembly and registers
ROP/JOP en hardening|ROP/JOP and hardening
Sneltoetsen en instellingen|Shortcuts and settings
Versie|Version
Alle rechten voorbehouden.|All rights reserved.
Eigen gebruiksvoorwaarden. Zie LICENSE.txt in de installatiemap.|Proprietary usage terms. See LICENSE.txt in the installation folder.
Taal wijzigen kan zodra de huidige taak en het programma gestopt zijn.|Stop the current task and program before changing the language.
Taalvoorkeur kon niet worden opgeslagen:|Could not save language preference:
'''

_pairs = [row.split('|', 1) for row in PAIRS.splitlines() if '|' in row]
_to_en = dict(_pairs)
_to_nl = {en: nl for nl, en in _pairs}
_patterns = {lang: re.compile('|'.join(('(?<!\\w)' if k[0].isalnum() else '') + re.escape(k) +
                                    ('(?!\\w)' if k[-1].isalnum() else '')
                                    for k in sorted(mapping, key=len, reverse=True)))
             for lang, mapping in [('en', _to_en), ('nl', _to_nl)]}

def tr(text):
    mapping = _to_en if language == 'en' else _to_nl
    return _patterns[language].sub(lambda match: mapping[match.group()], text)

def set_language(value):
    global language
    language = value if value in ('nl', 'en') else 'nl'
