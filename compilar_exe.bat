@echo off
echo [1/2] Limpiando compilaciones anteriores...
rmdir /s /q build dist 2>nul

echo [2/2] Compilando Sistema POS v2.0...
python -m PyInstaller --noconfirm --onedir --windowed ^
  --name "POS_Tienda" ^
  --paths "." ^
  --collect-all customtkinter ^
  --collect-submodules ui ^
  --collect-submodules bll ^
  --collect-submodules dal ^
  --hidden-import "win32print" ^
  --hidden-import "pywintypes" ^
  --hidden-import "sqlalchemy.dialects.sqlite" ^
  --hidden-import "PIL._tkinter_finder" ^
  main.py

echo.
if exist "dist\POS_Tienda\POS_Tienda.exe" (
    echo [OK] Compilacion exitosa: dist\POS_Tienda\POS_Tienda.exe
) else (
    echo [ERROR] Revisa los mensajes de arriba.
)
pause