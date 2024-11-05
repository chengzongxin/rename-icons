#!/bin/bash

# 检测操作系统并使用相应的激活命令
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows系统
    venv\Scripts\activate
else
    # Linux/macOS系统
    source venv/bin/activate
fi

# 运行程序，传递所有命令行参数
python image_renamer.py "$@"

# 检测操作系统并使用相应的退出命令
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows系统
    deactivate
else
    # Linux/macOS系统
    deactivate
fi 