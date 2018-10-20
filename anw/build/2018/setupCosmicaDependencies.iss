; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Cosmica Dependencies"
#define MyAppVersion "alpha"
#define MyAppPublisher "NeuroJump"
#define MyAppURL "www.playcosmica.com"
#define MyAppExeName "Cosmica Dependency Setup.exe"

[Code]
var
  WelcomePageID: Integer;
  BitmapImage: TBitmapImage;

procedure InitializeWizard;
var
  WelcomePage: TWizardPage;  
begin
  WelcomePage := CreateCustomPage(wpWelcome, '', '');
  WelcomePageID := WelcomePage.ID;
  BitmapImage := TBitmapImage.Create(WizardForm);
  BitmapImage.Bitmap.LoadFromFile('C:\Users\colsh\Downloads\development\ANW\anw\build\2018\cosmica.bmp');
  BitmapImage.Top := 0;
  BitmapImage.Left := 0;
  BitmapImage.AutoSize := True;
  BitmapImage.Cursor := crHand;
  BitmapImage.Visible := False;
  BitmapImage.Parent := WizardForm.InnerPage;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  BitmapImage.Visible := CurPageID = WelcomePageID;
  WizardForm.Bevel1.Visible := CurPageID <> WelcomePageID;
  WizardForm.MainPanel.Visible := CurPageID <> WelcomePageID;
  WizardForm.InnerNotebook.Visible := CurPageID <> WelcomePageID;
end;

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{962147EC-55DB-4A60-B0BF-6C079FE2B9A6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
CreateAppDir=no
OutputDir=C:\Users\colsh\Downloads\development\ANW\anw\build\2018
OutputBaseFilename=Cosmica Dependency Setup
SetupIconFile=C:\Users\colsh\Downloads\development\ANW\anw\build\2018\app.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "C:\Users\colsh\Downloads\development\ANW Setup\Panda3D-1.8.1.exe"; DestDir: "{win}"; Flags: ignoreversion
Source: "C:\Users\colsh\Downloads\development\ANW Setup\Twisted-15.3.0.win32-py2.7.exe"; DestDir: "{win}"; Flags: ignoreversion
Source: "C:\Users\colsh\Downloads\development\ANW Setup\zope.interface-4.1.3.win32-py2.7.exe"; DestDir: "{win}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Run]
Filename: "{app}\Panda3D-1.8.1.exe"; StatusMsg: "Installing Panda 3D"; Flags: skipifsilent
Filename: "{app}\Twisted-15.3.0.win32-py2.7.exe"; StatusMsg: "Installing Panda 3D"; Flags: skipifsilent
Filename: "{app}\zope.interface-4.1.3.win32-py2.7.exe"; StatusMsg: "Installing Panda 3D"; Flags: skipifsilent