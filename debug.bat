@echo off
:: start service
if "%1" == "startup" (
    if "%2" == "" (
        call :StartService all
    ) else (
        call :StartService %2
    )
) else (
    if "%1"=="" (
        call :StartService all
    )
)

:: close service
if "%1" == "shutdown" (
    if "%2" == "" (
        call :StopService all
    ) else (
        call :StopService %2
    )
)

:: restart service
if "%1" == "restart" (
    if "%2" == "" (
        call :StopService all
        call :StartService all
    ) else (
        call :StopService %2
        call :StartService %2
    )
)

:: ==============
:StartService
setlocal
    if "%~1" == "all" (
        start python web_manager.py
        start python monitor_manager.py
    ) else (
        start python %~1_manager.py
    )
endlocal
goto :eof

:StopService
setlocal
    if "%~1" == "all" (
        wmic process where "commandline like 'python%%_manager.py' or name='wechat.exe'" call terminate
    ) else (
        wmic process where "commandline like 'python%%%~1_manager.py'" call terminate
        if "%~1" == "web" (
            wmic process where "name='wechat.exe'" call terminate
        )
    )
endlocal
goto :eof