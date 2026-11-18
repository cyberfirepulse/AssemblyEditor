[Setup]
AppId=CyberFirePulse.AssemblyEditor
AppName=Assembly Editor
AppPublisher=CyberFirePulse
AppPublisherURL=https://github.com/cyberfirepulse
AppSupportURL=https://github.com/cyberfirepulse
AppVersion=5.5.7
VersionInfoVersion=5.5.7.0
DefaultDirName={localappdata}\Programs\AssemblyEditor
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=installer
OutputBaseFilename=AssemblyEditor_5.5.7_Setup
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
Source: "README.md"; DestDir: "{app}"
Source: "LICENSE.txt"; DestDir: "{app}"
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\Assembly Editor"; Filename: "{app}\AssemblyEditor.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\assembly-editor.ico"

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Icons]
Name: "{userdesktop}\Assembly Editor"; Filename: "{app}\AssemblyEditor.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\assembly-editor.ico"; Tasks: desktopicon
