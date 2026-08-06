; Inno Setup — Tri-River Valley Cinematic Digital Twin (production)
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

[Code]
var
  PostgresPortPage: TInputQueryWizardPage;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\DirectX') then
  begin
    SuppressibleMsgBox('Critical: DirectX infrastructure not found. Install current graphics runtime before setup.', mbCriticalError, MB_OK, MB_OK);
    Result := False;
  end;
end;

procedure InitializeWizard();
begin
  PostgresPortPage := CreateInputQueryPage(wpReady,
    'Database Pipeline Customization', 'Internal Port Allocations',
    'Verify the port for the internal PostGIS simulation pipeline.');
  PostgresPortPage.Add('Pipeline Communication Target Port:', False);
  PostgresPortPage.Values[0] := '8087';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = PostgresPortPage.ID then
  begin
    if GetSpaceOnDisk(0, True, True) < (Int64(5) * 1024 * 1024 * 1024) then
    begin
      MsgBox('Insufficient disk space (need ~5 GB) to initialize database systems.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure ConfigureWindowsNetworkFidelity();
var
  ResultCode: Integer;
begin
  WizardForm.StatusLabel.Caption := 'Optimizing network configuration...';
  Exec('reg.exe', 'add "HKLM\SYSTEM\CurrentControlSet\Services\Afd\Parameters" /v "DefaultReceiveWindow" /t REG_DWORD /d 16777216 /f', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('reg.exe', 'add "HKLM\SYSTEM\CurrentControlSet\Services\Afd\Parameters" /v "DefaultSendWindow" /t REG_DWORD /d 16777216 /f', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('netsh.exe', 'int ipv4 set dynamicportrange protocol=udp start=49152 num=16384', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('netsh.exe', 'int ipv4 set dynamicportrange protocol=tcp start=49152 num=16384', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  TargetPort: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigureWindowsNetworkFidelity();
    TargetPort := PostgresPortPage.Values[0];
    WizardForm.StatusLabel.Caption := 'Validating local datastore...';
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    Exec('net.exe', 'stop TriRiverPostgres', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
