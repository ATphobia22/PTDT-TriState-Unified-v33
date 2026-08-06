; Inno Setup script — Tri-River Valley Cinematic Digital Twin
[Setup]
AppName=Tri-River Valley Cinematic Digital Twin
AppVersion=33.0.0
AppPublisher=ATphobia22
DefaultDirName={autopf}\TriRiverDigitalTwin
DefaultGroupName=Tri-River Valley GIS
Compression=lzma2/max
SolidCompression=yes
OutputDir=.\installer_output
OutputBaseFilename=TriRiverTwin_Win11_Setup
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "..\release\PTDT-Unified-V33-Portable.exe"; DestDir: "{app}"; DestName: "TriStateDigitalTwin.exe"; Flags: ignoreversion
Source: "..\volumes\postgresql_init.d\*"; DestDir: "{app}\PostgresInit"; Flags: recursesubdirs

[Icons]
Name: "{group}\Tri-River Twin"; Filename: "{app}\TriStateDigitalTwin.exe"
Name: "{commondesktop}\Tri-River Twin"; Filename: "{app}\TriStateDigitalTwin.exe"

[Run]
Filename: "{app}\TriStateDigitalTwin.exe"; Description: "Launch Tri-River Twin"; Flags: nowait postinstall skipifsilent
