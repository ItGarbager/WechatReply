@echo off
:: start service
if "%1" == "startup" (
    if "%2" == "" (
        start python web_manager.py
        start python monitor_manager.py
    ) else (
        start python %2_manager.py & title=%2
    )
) else (
    if "%1"=="" (
        start python web_manager.py
        start python monitor_manager.py
    )
)
:: close service
if "%1" == "shutdown" (
    if "%2" == "" (
        wmic process where "commandline like 'python%%manager.py' or name='wechat.exe'" call terminate
    ) else (
        echo python %2_manager.py
        wmic process where "commandline like 'python%%%2_manager.py'" call terminate
        if "%2" == "web" (
            wmic process where "name='wechat.exe'" call terminate
        )
    )
)

goto :eof