#!/usr/bin/env python3

import requests
import os
from pathlib import Path
from PIL import Image
import time
import re
import sys
import argparse
from config import DEEPBRICKS_CONFIG
import base64

class AppIconRenamer:
    def __init__(self):
        """
        Initialize icon renamer with DeepBricks AI
        """
        # 从配置文件获取DeepBricks配置
        self.API_KEY = DEEPBRICKS_CONFIG['API_KEY']
        self.API_URL = DEEPBRICKS_CONFIG['API_URL']
        
        # Supported image formats
        self.image_extensions = ('.png', '.jpg', '.jpeg')
        
        # 移除了AipImageClassify的初始化

    def get_image_size(self, image_path):
        """Get image dimensions"""
        with Image.open(image_path) as img:
            return img.size

    def guess_density(self, width, height):
        """Guess image density based on size"""
        base_size = 24
        size = max(width, height)
        
        if size <= base_size:
            return ""
        elif size <= base_size * 2:
            return "@2x"
        else:
            return "@3x"

    def analyze_icon(self, image_path):
        """使用DeepBricks AI分析图片"""
        try:
            print(f"\n正在分析图片: {os.path.basename(image_path)}")
            
            # 获取图片尺寸
            width, height = self.get_image_size(image_path)
            density = self.guess_density(width, height)
            print(f"图片尺寸: {width}x{height}, 密度: {density}")
            
            # 准备API请求
            headers = {
                'Authorization': f'Bearer {self.API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # 读取图片并转换为base64
            with open(image_path, 'rb') as fp:
                image_data = base64.b64encode(fp.read()).decode('utf-8')
            
            # 准备请求数据
            data = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请分析这个图标的内容，用简短的英文关键词描述它的主要特征。然后给这个关键词添加密度标识，比如@2x，@3x等。如果原始图标是@2x，那么返回的结果应该是关键词@2x。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
            
            # 调用DeepBricks API
            print("\n正在调用DeepBricks AI API...")
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=data
            )
            
            result = response.json()
            print("\n=== API 返回结果详情 ===")
            print(f"原始返回: {result}")
            
            # 正确解析JSON结构
            if 'choices' in result and len(result['choices']) > 0:
                # 获取message中的content
                content = result['choices'][0]['message']['content']
                print(f"\n识别结果: {content}")
                
                # 直接使用content作为关键词（因为已经要求AI返回简短的关键词）
                cleaned_keyword = self._clean_name(content)
                
                if cleaned_keyword:
                    # 如果有密度标识，添加到文件名
                    final_name = f"{cleaned_keyword}{density}"
                    print(f"\n最终生成的名称: {final_name}")
                    return final_name
                else:
                    return 'unknown'
            else:
                print("\n警告: 无法从API返回结果中提取内容")
                if 'error' in result:
                    print(f"错误信息: {result['error']}")
                return 'unknown'
                
        except Exception as e:
            print(f"\n分析图片时发生错误: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            return 'unknown'

    def _clean_name(self, text):
        """
        Clean and format the name to be file-system friendly
        """
        try:
            # Convert to lowercase
            text = text.lower()
            # Remove special characters and extra spaces
            text = re.sub(r'[^\w\s-]', '', text)
            # Replace spaces and hyphens with underscores
            text = re.sub(r'[-\s]+', '_', text)
            # Remove common words that don't add meaning
            stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words = text.split('_')
            words = [w for w in words if w not in stop_words]
            # Limit word length
            words = [w[:15] for w in words]  # Limit each word to 15 chars
            # Join words back together
            text = '_'.join(words)
            # Remove leading/trailing underscores
            text = text.strip('_')
            return text
        except:
            return "unknown"

    def rename_icons(self, folder_path):
        """
        Batch rename icon files
        """
        if not os.path.exists(folder_path):
            print(f"错误：文件夹 '{folder_path}' 不存在！")
            return
        
        files = os.listdir(folder_path)
        name_counters = {}
        
        # Collect all rename operations
        rename_plans = []
        total_files = len([f for f in files if os.path.splitext(f)[1].lower() in self.image_extensions])
        current_file = 0
        
        for filename in files:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in self.image_extensions:
                current_file += 1
                print(f"\n处理第 {current_file}/{total_files} 个文件")
                print("=" * 50)
                
                old_path = os.path.join(folder_path, filename)
                
                # Analyze icon
                icon_prefix = self.analyze_icon(old_path)
                
                # Handle duplicate names
                if icon_prefix in name_counters:
                    name_counters[icon_prefix] += 1
                    icon_prefix = f"{icon_prefix}_{name_counters[icon_prefix]}"
                    print(f"检测到重复名称，添加后缀: {icon_prefix}")
                else:
                    name_counters[icon_prefix] = 0
                
                # Build new filename
                new_filename = f"{icon_prefix}{file_ext}"
                new_path = os.path.join(folder_path, new_filename)
                
                print(f"\n计划重命名:")
                print(f"原文件名: {filename}")
                print(f"新文件名: {new_filename}")
                print("=" * 50)
                
                rename_plans.append((old_path, new_path, filename, new_filename))
                
                # Avoid frequent API calls
                if current_file < total_files:
                    print("\n等待0.5秒后处理下一个文件...")
                    time.sleep(0.5)
        
        # Execute rename operations
        if rename_plans:
            print("\n\n开始执行重命名操作:")
            print("=" * 50)
            
            for old_path, new_path, old_name, new_name in rename_plans:
                try:
                    if os.path.exists(new_path):
                        print(f"警告: 文件 '{new_name}' 已存在，跳过重命名 '{old_name}'")
                        continue
                        
                    os.rename(old_path, new_path)
                    print(f"成功重命名: {old_name} -> {new_name}")
                except Exception as e:
                    print(f"重命名 {old_name} 时发���错误: {str(e)}")
            
            print("\n重命名操作完成！")
        else:
            print("\n没有找到需要重命名的图片文件。")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='批量重命名图标文件')
    parser.add_argument('path', nargs='?', default='.',
                      help='图标文件夹路径 (默认为当前目录)')
    parser.add_argument('-r', '--recursive', action='store_true',
                      help='递归处理子文件夹')
    parser.add_argument('-p', '--preview', action='store_true',
                      help='预览模式，显示将要进行的重命名操作但不实际执行')
    
    args = parser.parse_args()
    
    # 获取并处理路径
    folder_path = args.path.strip()
    
    # 如果是拖拽的路径，除可能的引号
    if folder_path.startswith('"') and folder_path.endswith('"'):
        folder_path = folder_path[1:-1]
    
    # 转换为绝对路径
    folder_path = os.path.abspath(folder_path)
    
    # 检查路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误：文件夹 '{folder_path}' 不存在！")
        return
    
    # 显示当前工作目录
    print(f"工作目录: {folder_path}")
    
    # 创建重命名器实例
    renamer = AppIconRenamer()
    
    # 执行重命名
    if args.preview:
        print("预览模式：")
    renamer.rename_icons(folder_path)

if __name__ == "__main__":
    main() 