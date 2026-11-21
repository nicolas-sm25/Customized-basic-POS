[Setup]
AppName=Sistema POS Tienda
AppVersion=2.0.1
DefaultDirName={autopf}\POS_Tienda
DefaultGroupName=Sistema POS Tienda
OutputDir=Output
OutputBaseFilename=Instalador_POS_v2.0.1
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el Escritorio"; GroupDescription: "Accesos directos:"

[Files]
; 1. Empaqueta todo el Sistema POS compilado por PyInstaller
Source: "dist\POS_Tienda\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. Empaqueta el driver de la impresora SAT en una carpeta temporal y lo borra al terminar
Source: "drivers\SAT POS Printer Driver v2.7.1.4.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\Sistema POS Tienda"; Filename: "{app}\POS_Tienda.exe"
Name: "{group}\Desinstalar Sistema POS"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Sistema POS Tienda"; Filename: "{app}\POS_Tienda.exe"; Tasks: desktopicon

[Run]
; Paso A: Lanza el instalador del driver SAT y espera a que termine antes de abrir el POS
Filename: "{tmp}\SAT POS Printer Driver v2.7.1.4.exe"; Description: "Instalar driver de impresora térmica SAT Q23T"; Flags: postinstall waituntilterminated

; Paso B: Abre el Sistema POS ya con la impresora instalada en Windows
Filename: "{app}\POS_Tienda.exe"; Description: "Abrir Sistema POS ahora"; Flags: nowait postinstall skipifsilent