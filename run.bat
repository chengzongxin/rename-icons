@echo off
:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 运行Python程序
python image_renamer.py %*

:: 退出虚拟环境
deactivate 