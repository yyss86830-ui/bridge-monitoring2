@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\pythonw.exe" (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.Windows.MessageBox]::Show('Run setup.bat once first.','Bridge Monitor')"
  exit /b 1
)
start "" "venv\Scripts\pythonw.exe" "app.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"
exit
