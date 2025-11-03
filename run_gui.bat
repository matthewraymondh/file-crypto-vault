@echo off
title File Crypto - GUI Application

echo ============================================
echo Starting File Crypto GUI...
echo ============================================
echo.

python crypto_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo Error occurred! Check if dependencies are installed.
    echo Run install_dependencies.bat first.
    echo ============================================
    pause
)
