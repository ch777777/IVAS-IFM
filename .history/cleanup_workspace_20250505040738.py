#!/usr/bin/env python
"""
工作区清理工具
用于清理工作区中的带时间戳文件

用法:
    python cleanup_workspace.py [--dry-run]
"""
import os
import re
import argparse
import shutil
from pathlib import Path
from datetime import datetime

def find_timestamped_files(directory):
    """查找带时间戳的文件"""
    timestamp_pattern = re.compile(r'.*_\d{14}\.\w+$')
    result = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if timestamp_pattern.match(file):
                result.append(os.path.join(root, file))
    
    return result

def find_duplicates_by_base_name(files):
    """根据基本名称分组文件"""
    file_groups = {}
    
    for file_path in files:
        filename = os.path.basename(file_path)
        # 提取基本名称 (去除时间戳部分)
        base_name = re.sub(r'_\d{14}(\.\w+)$', r'\1', filename)
        
        if base_name not in file_groups:
            file_groups[base_name] = []
        
        file_groups[base_name].append(file_path)
    
    # 只保留有多个版本的文件组
    return {k: v for k, v in file_groups.items() if len(v) > 1}

def find_latest_files(file_groups):
    """找出每组中的最新文件"""
    latest_files = {}
    
    for base_name, files in file_groups.items():
        # 按修改时间排序
        sorted_files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
        latest_files[base_name] = sorted_files[0]
    
    return latest_files

def cleanup_workspace(dry_run=False):
    """清理工作区"""
    # 获取当前目录
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"扫描工作区: {workspace_dir}")
    timestamped_files = find_timestamped_files(workspace_dir)
    
    if not timestamped_files:
        print("未找到带时间戳的文件")
        return
    
    print(f"找到 {len(timestamped_files)} 个带时间戳的文件")
    
    # 按基本名称分组
    file_groups = find_duplicates_by_base_name(timestamped_files)
    
    if not file_groups:
        print("未找到需要清理的文件组")
        return
    
    # 找出每组中的最新文件
    latest_files = find_latest_files(file_groups)
    
    # 创建备份目录
    backup_dir = os.path.join(workspace_dir, "old_timestamps")
    if not dry_run and not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 处理每组文件
    for base_name, group in file_groups.items():
        latest_file = latest_files[base_name]
        target_file = os.path.join(workspace_dir, base_name)
        
        print(f"\n处理文件组: {base_name}")
        print(f"- 最新文件: {os.path.basename(latest_file)}")
        
        # 复制最新文件到目标位置
        if not dry_run:
            try:
                shutil.copy2(latest_file, target_file)
                print(f"- 已复制到: {target_file}")
            except Exception as e:
                print(f"- 复制失败: {e}")
                continue
        else:
            print(f"- 将复制到: {target_file} (模拟运行)")
        
        # 移动所有文件到备份目录
        for file_path in group:
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            
            if not dry_run:
                try:
                    shutil.move(file_path, backup_path)
                    print(f"- 已移动到备份: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"- 移动失败: {e}")
            else:
                print(f"- 将移动到备份: {os.path.basename(file_path)} (模拟运行)")
    
    if dry_run:
        print("\n这是模拟运行，未执行实际操作")
    else:
        print(f"\n清理完成! 所有时间戳文件已移至: {backup_dir}")

def main():
    parser = argparse.ArgumentParser(description='清理工作区中的带时间戳文件')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不执行实际操作')
    
    args = parser.parse_args()
    cleanup_workspace(dry_run=args.dry_run)

if __name__ == "__main__":
    main() 