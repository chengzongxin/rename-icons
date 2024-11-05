#!/usr/bin/env python3

import requests
import os
from pathlib import Path
from PIL import Image
import time
import re
import sys
import argparse
from config import DEEPAI_CONFIG

class AppIconRenamer:
    def __init__(self):
        """
        Initialize icon renamer with DeepAI
        """
        self.API_KEY = DEEPAI_CONFIG['API_KEY']
        self.API_ENDPOINT = 'https://api.deepai.org/api/text2img'
        
        # Supported image formats
        self.image_extensions = ('.png', '.jpg', '.jpeg')

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
        """
        Analyze icon using DeepAI
        """
        try:
            print(f"\n正在分析图片: {os.path.basename(image_path)}")
            
            # Get image size
            width, height = self.get_image_size(image_path)
            density = self.guess_density(width, height)
            print(f"图片尺寸: {width}x{height}, 密度: {density}")
            
            # Prepare the API request
            headers = {
                'api-key': self.API_KEY
            }
            
            print("正在调用 DeepAI API...")
            
            # Send image for analysis
            with open(image_path, 'rb') as file:
                response = requests.post(
                    self.API_ENDPOINT,
                    files={'image': file},
                    headers=headers
                )
            
            if response.status_code == 200:
                result = response.json()
                print("API 返回结果:")
                print(result)
                
                name_parts = []
                
                # 从不同字段获取信息
                if 'output' in result:
                    output = result['output']
                    
                    # 尝试从主要描述中获取信息
                    if 'general_description' in output:
                        main_desc = output['general_description']
                        print(f"\n主要描述: {main_desc}")
                        cleaned_desc = self._clean_name(main_desc)
                        if cleaned_desc:
                            name_parts.append(cleaned_desc)
                    
                    # 从标签中获取补充信息
                    if 'tags' in output:
                        tags = output['tags']
                        if tags:
                            print("\n识别到的标签:")
                            for i, tag in enumerate(tags[:3], 1):
                                print(f"{i}. {tag}")
                            
                            # 使用最相关的标签
                            if tags[0] not in main_desc:
                                cleaned_tag = self._clean_name(tags[0])
                                if cleaned_tag and cleaned_tag not in name_parts:
                                    print(f"添加补充标签: {cleaned_tag}")
                                    name_parts.append(cleaned_tag)
                
                if name_parts:
                    # Combine parts
                    final_name = '_'.join(name_parts[:2])  # 限制为两个部分
                    print(f"\n最终文件名: ic_{final_name}{density}")
                    return f"ic_{final_name}", density
                
                return "ic_unknown", density
            
            else:
                print(f"API 调用失败: {response.status_code}")
                print(response.text)
                return "ic_unknown", density
                
        except Exception as e:
            print(f"分析图片时发生错误: {str(e)}")
            return "ic_unknown", ""

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
                icon_prefix, density = self.analyze_icon(old_path)
                
                # Handle duplicate names
                if icon_prefix in name_counters:
                    name_counters[icon_prefix] += 1
                    icon_prefix = f"{icon_prefix}_{name_counters[icon_prefix]}"
                    print(f"检测到重复名称，添加后缀: {icon_prefix}")
                else:
                    name_counters[icon_prefix] = 0
                
                # Build new filename
                new_filename = f"{icon_prefix}{density}{file_ext}"
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
                    print(f"重命名 {old_name} 时发生错误: {str(e)}")
            
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