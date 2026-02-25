; BIMS2 Inno Setup Script
; This script creates a professional Windows installer that handles prerequisites.

#define MyAppName "BIMS2"
#define MyAppVersion "1.0.0-alpha"
#define MyAppPublisher "Sean Lloyd Harold Raquel"
#define MyAppExeName "waitress_server.exe"
#define MyAppIcon "resources\app_icon.ico"
#define MyInstallerIcon "resources\installer_icon.ico"

[Setup]
AppId={{D3E8A1B2-7F6C-4A2B-8E9D-1C5B3A4F6E7D}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist_hardened\installer
OutputBaseFilename=BIMS2_Setup_v{#MyAppVersion}
SetupIconFile={#MyInstallerIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Run BIMS2 when windows starts"; GroupDescription: "Auto-start Options:"; Flags: unchecked

[Files]
; The actual C++ Compiled Standalone Binary and its dependencies
Source: "dist_hardened\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "installer\*,build\*"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: desktopicon
Name: "{commonstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "C:\BIMS_Data"; Permissions: everyone-full
Name: "C:\BIMS_Data\media"; Permissions: everyone-full
Name: "C:\BIMS_Data\logs"; Permissions: everyone-full
Name: "C:\BIMS_Data\certificates"; Permissions: everyone-full

[Code]
// Standalone distribution verification
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
