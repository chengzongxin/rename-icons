#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 运行程序，传递所有命令行参数
python image_renamer.py "$@"

# 退出虚拟环境
deactivate 