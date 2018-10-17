; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Armada Wars"
#define MyAppVersion "0.14.0"
#define MyAppPublisher "NeuroJump"
#define MyAppURL "https://neurojump.ca"
#define MyGameSourcePath "C:\Users\colsh\Downloads\development\ANW\anw"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{D66402ED-CA2B-4F6E-92F8-BF6F09296F56}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=C:\Users\colsh\Downloads\development\ANW\anw\build\2018\license.txt
InfoBeforeFile=C:\Users\colsh\Downloads\development\ANW\anw\build\2018\release.txt
OutputDir=C:\Users\colsh\Downloads\development\ANW\anw\build\2018
OutputBaseFilename=ArmadaWars-0.14.0
SetupIconFile=C:\Users\colsh\Downloads\development\ANW\anw\build\2018\ANW.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyGameSourcePath}\Client\*"; DestDir: "{app}\Client"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full
Source: "{#MyGameSourcePath}\Data\*"; DestDir: "{app}\Data"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full
Source: "{#MyGameSourcePath}\Database\*"; DestDir: "{app}\Database"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full
Source: "{#MyGameSourcePath}\Packages\*"; DestDir: "{app}\Packages"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full
Source: "{#MyGameSourcePath}\Server\*"; DestDir: "{app}\Server"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{userdesktop}\Armada Wars Single Player"; Filename: "{app}\Client\singleplayer.bat"; \
    IconFilename: "{app}\Client\logo.ico"; Tasks: desktopicon
Name: "{userdesktop}\Armada Wars Join Game 1"; Filename: "{app}\Client\startclient1.bat"; \
    IconFilename: "{app}\Client\logo.ico"; Tasks: desktopicon
Name: "{userdesktop}\Armada Wars Host Game 1"; Filename: "{app}\Client\startserver1.bat"; \
    IconFilename: "{app}\Client\logo.ico"; Tasks: desktopicon
Name: "{userdesktop}\Armada Wars Folder Location"; Filename: "{app}\Client\"; Tasks: desktopicon; Flags: foldershortcut;

