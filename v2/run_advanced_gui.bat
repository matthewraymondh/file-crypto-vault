@echo off
title Advanced File Crypto - GUI Application

echo ============================================
echo Starting Advanced File Crypto GUI v2.0...
echo ============================================
echo.

python crypto_gui_advanced.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo Error occurred! Check if dependencies are installed.
    echo Run install_dependencies.bat first.
    echo ============================================
    pause
)
