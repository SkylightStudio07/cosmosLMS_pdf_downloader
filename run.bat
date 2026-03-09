@echo off
cd /d "%~dp0"
python gui.py
if %errorlevel% neq 0 (
    echo.
    echo 오류가 발생했습니다. 위 내용을 확인해주세요.
    pause
)
