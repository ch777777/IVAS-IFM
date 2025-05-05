"""
文件管理工具
提供文件版本控制和更新功能，避免创建多个带时间戳的文件
"""
import os
import datetime
import re
import shutil
from pathlib import Path

def get_version_info():
    """
    从config/settings.py获取当前版本信息
    
    Returns:
        dict: 包含版本号和构建日期的字典
    """
    try:
        from ..config.settings import VERSION, BUILD_DATE
        return {
            "version": VERSION,
            "build_date": BUILD_DATE
        }
    except ImportError:
        # 如果无法导入，返回默认值
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return {
            "version": "1.0.0",
            "build_date": today
        }

def update_document(file_path, new_content, backup=True):
    """
    更新文档文件，保留可选的备份
    
    Args:
        file_path (str): 文档路径
        new_content (str): 新的文档内容
        backup (bool, optional): 是否创建备份。默认为True
    
    Returns:
        bool: 更新是否成功
    """
    file_path = Path(file_path)
    
    # 确保目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果文件存在且需要备份
    if file_path.exists() and backup:
        backup_dir = file_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        shutil.copy2(file_path, backup_file)
    
    # 写入新内容
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"更新文件失败: {e}")
        return False

def add_version_to_document(content, doc_type):
    """
    在文档中添加或更新版本信息
    
    Args:
        content (str): 文档内容
        doc_type (str): 文档类型 (如 'README', 'ARCHITECTURE')
    
    Returns:
        str: 更新后的文档内容
    """
    version_info = get_version_info()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    version_header = f"# {doc_type} (版本 {version_info['version']} - {today})\n"
    
    # 替换第一行（假设第一行是标题）
    lines = content.split('\n')
    if lines and lines[0].startswith('# '):
        lines[0] = version_header
        return '\n'.join(lines)
    else:
        # 如果找不到标题行，在开头添加版本信息
        return version_header + content

def find_documents_by_pattern(directory, pattern):
    """
    在目录中查找匹配模式的文档
    
    Args:
        directory (str): 要搜索的目录
        pattern (str): 文件名模式（正则表达式）
    
    Returns:
        list: 匹配的文件路径列表
    """
    matched_files = []
    pattern_re = re.compile(pattern)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if pattern_re.match(file):
                matched_files.append(os.path.join(root, file))
    
    return matched_files

def cleanup_timestamped_files(directory, base_filename, keep_latest=True):
    """
    清理带时间戳的文件，保留最新版本
    
    Args:
        directory (str): 要清理的目录
        base_filename (str): 基本文件名（不含时间戳）
        keep_latest (bool, optional): 是否保留最新版本。默认为True
    
    Returns:
        int: 删除的文件数量
    """
    pattern = f"{base_filename}_\\d+\\.md"
    matched_files = find_documents_by_pattern(directory, pattern)
    
    if not matched_files:
        return 0
    
    # 按修改时间排序
    matched_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # 如果需要保留最新版本，从列表中排除
    files_to_delete = matched_files[1:] if keep_latest and matched_files else matched_files
    
    # 删除文件
    for file in files_to_delete:
        try:
            os.remove(file)
        except OSError:
            pass
    
    return len(files_to_delete)

def migrate_to_single_file_system(workspace_dir):
    """
    将多个带时间戳的文件合并为单个文件
    
    Args:
        workspace_dir (str): 工作区目录
    
    Returns:
        dict: 迁移结果摘要
    """
    result = {
        "migrated_files": 0,
        "deleted_files": 0,
        "errors": 0
    }
    
    # 定义要处理的文件类型
    file_types = [
        {"pattern": r"ARCHITECTURE_\d+\.md", "target": "ARCHITECTURE.md", "type": "ARCHITECTURE"},
        {"pattern": r"README_\d+\.md", "target": "README.md", "type": "README"},
        {"pattern": r"requirements_\d+\.txt", "target": "requirements.txt", "type": None},
        {"pattern": r"build_\d+\.bat", "target": "build.bat", "type": None}
    ]
    
    for file_type in file_types:
        pattern = file_type["pattern"]
        target = file_type["target"]
        doc_type = file_type["type"]
        
        # 查找匹配的文件
        matched_files = find_documents_by_pattern(workspace_dir, pattern)
        
        if not matched_files:
            continue
        
        # 按修改时间排序，取最新的
        matched_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_file = matched_files[0]
        
        try:
            # 读取最新文件内容
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果是文档类型，添加版本信息
            if doc_type:
                content = add_version_to_document(content, doc_type)
            
            # 更新到目标文件
            target_path = os.path.join(workspace_dir, target)
            update_document(target_path, content)
            
            # 删除所有时间戳文件
            for file in matched_files:
                try:
                    os.remove(file)
                    result["deleted_files"] += 1
                except OSError:
                    result["errors"] += 1
            
            result["migrated_files"] += 1
            
        except Exception as e:
            print(f"处理文件失败 {latest_file}: {e}")
            result["errors"] += 1
    
    return result 
 