@echo off
title Conecta 4 - PC Python
cd /d "%~dp0"
python conecta4.py
if %errorlevel% neq 0 (
    py conecta4.py
)

