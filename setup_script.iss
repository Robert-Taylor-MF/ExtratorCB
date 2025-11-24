; Script gerado para Inno Setup
; Documentação: http://www.jrsoftware.org/ishelp/

#define MyAppName "ExtratorCB"
#define MyAppVersion "1.0"
#define MyAppPublisher "Robert Taylor de M. Ferreira"
#define MyAppURL "https://github.com/Robert-Taylor-MF/ExtratorCB"
#define MyAppExeName "ExtratorCB.exe"

[Setup]
; --- Identificação ---
AppId={{A1B2C3D4-E5F6-7890-1234-56789ABCDEF0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; --- Instalação ---
; Onde vai instalar por padrão (Arquivos de Programas)
DefaultDirName={autopf}\{#MyAppName}
; Nome do grupo no Menu Iniciar
DefaultGroupName={#MyAppName}
; Não permite o usuário escolher outra pasta (opcional, mude para no se quiser dar liberdade)
DisableDirPage=no

; --- Aparência do Instalador ---
; Nome do arquivo final gerado (ex: Instalador_ExtratorCB_v1.exe)
OutputBaseFilename=Instalador_ExtratorCB_v1
; Ícone do próprio instalador
SetupIconFile=assets\icone.ico
; Compressão máxima para o arquivo ficar pequeno
Compression=lzma
SolidCompression=yes
; Estilo moderno (Windows 10/11)
WizardStyle=modern

; --- Saída ---
; Onde o instalador será salvo (na raiz do projeto)
OutputDir=.

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; O arquivo principal (o executável que geramos com PyInstaller)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Se você quiser incluir o arquivo README ou Manual junto na pasta de instalação:
Source: "docs\MANUAL_DE_USO.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Atalho no Menu Iniciar
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Atalho para desinstalar
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Atalho na Área de Trabalho (Desktop)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Opção para rodar o programa logo após instalar
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent