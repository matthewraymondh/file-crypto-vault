@echo off
echo ============================================
echo Installing File Crypto Dependencies
echo ============================================
echo.

echo Installing Python packages...
pip install -r requirements.txt

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo To run the GUI application, execute:
echo     python crypto_gui.py
echo.
pause
