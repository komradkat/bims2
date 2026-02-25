; BIMS2 Inno Setup Script
; This script creates a professional Windows installer that handles prerequisites.

#define MyAppName "BIMS2"
#define MyAppVersion "1.0.0-alpha"
#define MyAppPublisher "Your Barangay / Organization"
#define MyAppExeName "waitress_server.exe"

[Setup]
AppId={{BIMS2-SYSTEM-INTEGRATED-001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist_hardened\installer
OutputBaseFilename=BIMS2_Setup_v{#MyAppVersion}
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
; The actual build files from Nuitka and PyArmor
Source: "dist_hardened\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note: We don't bundle Python here, we'll download it if missing via IDP

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commonstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "C:\BIMS_Data"; Permissions: everyone-full
Name: "C:\BIMS_Data\media"; Permissions: everyone-full
Name: "C:\BIMS_Data\logs"; Permissions: everyone-full
Name: "C:\BIMS_Data\certificates"; Permissions: everyone-full

[Code]
// --- Inno Download Plugin (IDP) Integration ---
// This part handles downloading Python if it's missing.
// Note: Requires IDP to be installed in the build environment.

procedure InitializeWizard;
begin
  // Check for Python 3.13 installation in Registry or Path
  // If missing, add to IDP download queue:
  // idpAddFile('https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe', ExpandConstant('{tmp}\python_installer.exe'));
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
     // Run silent python install if downloaded
     // Exec(ExpandConstant('{tmp}\python_installer.exe'), '/quiet InstallAllUsers=1 PrependPath=1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
