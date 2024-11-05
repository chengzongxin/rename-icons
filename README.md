# Icon Renamer

一个基于 AI 的图标文件批量重命名工具。使用 DeepBricks AI 来分析图标内容并生成有意义的文件名。

## 功能特点

- 自动分析图标内容并生成描述性文件名
- 自动检测图标密度(@1x/@2x/@3x)
- 支持批量处理
- 支持多种图片格式(PNG, JPG, JPEG)
- 防止文件名冲突
- 预览模式支持

## 环境要求

- Python 3.x
- pip (Python包管理器)
- DeepBricks AI API密钥 (https://deepbricks.ai/)

## 依赖库

- requests
- Pillow (PIL)
- pathlib

## 安装步骤

1. 克隆仓库：

```bash
git clone [repository-url]
cd icon-renamer

2. 创建并激活虚拟环境：


Windows
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux
```bash
python -m venv venv
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```


4. 配置API密钥：
   - 复制 `config.example.py` 为 `config.py`
   - 在 `config.py` 中填入您的 DeepBricks API 密钥
   ```python
   # config.py
   DEEPBRICKS_CONFIG = {
       'API_KEY': 'your-api-key-here',  # 替换为您的API密钥
       'API_URL': 'https://api.deepbricks.ai/v1/chat/completions'
   }
   ```

## 使用方法

### 命令行参数

```bash
python image_renamer.py [options]
```


参数说明：
- `path`: 图标文件夹路径（默认：当前目录）
- `-r, --recursive`: 递归处理子文件夹
- `-p, --preview`: 预览模式，不实际执行重命名

### 使用示例

1. 处理当前目录的图标：

```bash
python image_renamer.py
```


3. 递归处理文件夹：

```bash
python image_renamer.py /path/to/icons -r
```


### 使用脚本运行

Windows:
```bash
.\run.bat
```

macOS/Linux:
```bash
./run.sh
```
```bash
chmod +x run.sh # 首次使用前添加执行权限
./run.sh [参数]
```


## 文件命名规则

- 基于AI识别的图标内容生成英文关键词
- 自动添加密度标识：
  - 小于等于24px: 无标识
  - 24px-48px: @2x
  - 大于48px: @3x
- 特殊字符处理：
  - 转换为小写
  - 空格和连字符转换为下划线
  - 移除特殊字符
  - 移除常见虚词(a, an, the等)
- 文件名长度限制：每个单词最多15字符

## 注意事项

1. API 使用
   - 确保 API 密钥配置正确
   - 注意 API 调用频率限制
   - 大量图片处理时建议分批进行

2. 文件处理
   - 建议先使用预览模式(-p)测试
   - 重要文件建议先备份
   - 确保对目标文件夹有写入权限

3. 性能考虑
   - 程序会在每次API调用之间等待0.5秒
   - 处理大量图片时可能需要较长时间

## 常见问题

1. 配置问题
   - Q: 如何获取 API 密钥？
   - A: 访问 https://deepbricks.ai/ 注册账号并获取密钥

2. 运行错误
   - Q: 提示 "无法从API返回结果中提取内容"？
   - A: 检查网络连接和 API 密钥是否正确

3. 文件问题
   - Q: 某些图片没有被重命名？
   - A: 检查文件格式是否支持，以及文件是否被其他程序占用

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request