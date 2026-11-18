[Setup]
AppId=CyberFirePulse.AssemblyEditor
AppName=Assembly Editor
AppPublisher=CyberFirePulse
AppPublisherURL=https://github.com/cyberfirepulse
AppSupportURL=https://github.com/cyberfirepulse
AppVersion=5.5.9
VersionInfoVersion=5.5.9.0
DefaultDirName={autopf}\AssemblyEditor
DefaultGroupName=Assembly Editor
DisableDirPage=no
DisableProgramGroupPage=no
DisableWelcomePage=no
UsePreviousPrivileges=no
PrivilegesRequiredOverridesAllowed=dialog
AppUpdatesURL=https://github.com/cyberfirepulse/AssemblyEditor/releases
AppContact=cyberfirepulse@gmail.com
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=installer
OutputBaseFilename=AssemblyEditor_5.5.9_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
WizardResizable=yes
SetupIconFile=assets\cyberfirepulse.ico
WizardImageFile=assets\cyberfirepulse-wizard.bmp
WizardSmallImageFile=assets\cyberfirepulse-small.bmp
UninstallDisplayIcon={app}\AssemblyEditor.exe

[Files]
Source: "dist\AssemblyEditor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"
Source: "LICENSE.txt"; DestDir: "{app}"
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\Assembly Editor"; Filename: "{app}\AssemblyEditor.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\assembly-editor.ico"

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"; LicenseFile: "docs\LICENSE_nl.txt"; InfoBeforeFile: "docs\INFO_BEFORE_nl.txt"; InfoAfterFile: "docs\DISCLAIMER_nl.txt"
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "docs\LICENSE_en.txt"; InfoBeforeFile: "docs\INFO_BEFORE_en.txt"; InfoAfterFile: "docs\DISCLAIMER_en.txt"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Icons]
Name: "{autodesktop}\Assembly Editor"; Filename: "{app}\AssemblyEditor.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\assembly-editor.ico"; Tasks: desktopicon

[Icons]
Name: "{group}\{cm:UninstallProgram,Assembly Editor}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\AssemblyEditor.exe"; Description: "{cm:LaunchProgram,Assembly Editor}"; Flags: nowait postinstall skipifsilent runasoriginaluser
