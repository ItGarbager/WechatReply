@echo off

:: 启动服务
if "%1"=="start" (
    if "%2" == "" (
        start python web_manager.py
        start python monitor_manager.py
    ) else (
        start python %2_manager.py
    )
) else (
    if "%1"=="" (
        echo sss
        start python web_manager.py
        start python monitor_manager.py
    )
)

:: 关闭服务
if "%1"=="stop" (
    if "%2" == "" (
        taskkill /F /IM python.exe
        echo 已关闭所有的python进程
        taskkill /F /IM WeChat.exe
        echo 已关闭所有的wechat进程
    ) else (
        taskkill /F /IM %2.exe
        echo 已关闭所有的%2进程
    )
)

goto :eof