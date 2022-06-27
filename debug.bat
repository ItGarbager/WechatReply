@echo off

:: start service
if "%1"=="startup" (
    if "%2" == "" (
        start python web_manager.py
        start python monitor_manager.py
    ) else (
        start python %2_manager.py
    )
) else (
    if "%1"=="" (
        start python web_manager.py
        start python monitor_manager.py
    )
)

:: close service
if "%1"=="shutdown" (
    if "%2" == "" (
        taskkill /F /IM python.exe
        echo Closed all Python processes
        taskkill /F /IM WeChat.exe
        echo Closed all WeChat processes
    ) else (
        taskkill /F /IM %2.exe
        echo Closed all WeChat %2 processes
    )
)

goto :eof