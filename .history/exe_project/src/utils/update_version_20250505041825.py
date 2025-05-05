"""
版本更新工具
用于更新文档版本信息并清理带时间戳的文件
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加上级目录到路径，确保正确导入
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入文件管理工具
try:
    from src.utils.file_manager import (
        get_version_info,
        update_document,
        add_version_to_document,
        find_documents_by_pattern,
        cleanup_timestamped_files,
        migrate_to_single_file_system
    )
except ImportError:
    # 如果从命令行直接运行，使用相对导入
    from .file_manager import (
        get_version_info,
        update_document,
        add_version_to_document,
        find_documents_by_pattern,
        cleanup_timestamped_files,
        migrate_to_single_file_system
    )

def update_version_in_file(file_path, version, build_date=None):
    """
    更新文件中的版本信息
    
    Args:
        file_path (str): 要更新的文件路径
        version (str): 新版本号
        build_date (str, optional): 构建日期. 默认为当前日期.
    
    Returns:
        bool: 更新是否成功
    """
    if build_date is None:
        build_date = datetime.now().strftime("%Y-%m-%d")
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"错误: 文件不存在 - {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 根据文件类型更新版本
        if file_path.suffix == '.py' and file_path.name == 'settings.py':
            # 更新设置文件中的版本号
            new_content = update_settings_version(content, version, build_date)
        elif file_path.suffix == '.md' and file_path.name == 'VERSION_TRACKER.md':
            # 更新版本跟踪文件
            new_content = update_version_tracker(content, version, build_date)
        elif file_path.suffix == '.md' and file_path.name == 'PROJECT_PLAN.md':
            # 更新项目计划文件
            new_content = update_project_plan(content, version, build_date)
        else:
            # 其他文档文件
            file_type = file_path.stem.upper()
            new_content = add_version_to_document(content, file_type)
        
        # 写入新内容
        return update_document(file_path, new_content)
    
    except Exception as e:
        print(f"更新版本信息失败: {e}")
        return False

def update_settings_version(content, version, build_date):
    """
    更新settings.py中的版本信息
    
    Args:
        content (str): 文件内容
        version (str): 新版本号
        build_date (str): 构建日期
    
    Returns:
        str: 更新后的内容
    """
    lines = content.split('\n')
    result = []
    
    for line in lines:
        if line.startswith('VERSION = '):
            result.append(f'VERSION = "{version}"')
        elif line.startswith('BUILD_DATE = '):
            result.append(f'BUILD_DATE = "{build_date}"')
        elif line.startswith('PREVIOUS_VERSION = '):
            # 获取当前版本作为前一版本
            current_version = None
            for l in lines:
                if l.startswith('VERSION = '):
                    current_version = l.split('=')[1].strip().strip('"\'')
                    break
            
            if current_version:
                result.append(f'PREVIOUS_VERSION = "{current_version}"')
            else:
                result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def update_version_tracker(content, version, build_date):
    """
    更新VERSION_TRACKER.md
    
    Args:
        content (str): 文件内容
        version (str): 新版本号
        build_date (str): 构建日期
    
    Returns:
        str: 更新后的内容
    """
    lines = content.split('\n')
    in_current_version_table = False
    current_version_found = False
    result = []
    
    for line in lines:
        # 更新版本表格
        if '| 版本号 | 发布日期 | 状态 | 说明 |' in line:
            in_current_version_table = True
            result.append(line)
        elif in_current_version_table and '|-------|---------|------|------|' in line:
            result.append(line)
        elif in_current_version_table and not current_version_found and '| ' in line:
            # 添加新版本行
            result.append(f'| {version} | {build_date} | 当前版本 | 已更新 |')
            
            # 将原当前版本标记为前一版本
            parts = line.split('|')
            if len(parts) >= 5:
                parts[3] = ' 前一版本 '
                result.append('|'.join(parts))
            
            current_version_found = True
            in_current_version_table = False
        else:
            result.append(line)
    
    # 如果找不到版本表格，则保持原样
    if not current_version_found:
        return content
    
    # 更新当前版本部分标题
    content = '\n'.join(result)
    current_version_section = f"## 当前版本 ({version}) 更新内容"
    previous_version_section = "## 前一版本"
    
    # 替换当前版本部分标题
    for section in ["## 当前版本", "## 当前版本 ("]:
        if section in content:
            start_idx = content.find(section)
            end_idx = content.find(")", start_idx) + 1 if "(" in section else content.find("\n", start_idx)
            content = content[:start_idx] + current_version_section + content[end_idx:]
            break
    
    return content

def update_project_plan(content, version, build_date):
    """
    更新PROJECT_PLAN.md
    
    Args:
        content (str): 文件内容
        version (str): 新版本号
        build_date (str): 构建日期
    
    Returns:
        str: 更新后的内容
    """
    lines = content.split('\n')
    result = []
    
    # 更新项目概述中的版本号
    in_project_overview = False
    for line in lines:
        if '## 项目概述' in line:
            in_project_overview = True
            result.append(line)
        elif in_project_overview and '| 当前版本 |' in line:
            # 替换版本信息行
            result.append(f'| 当前版本 | {version} |')
        elif in_project_overview and line.startswith('## '):
            # 下一个章节开始
            in_project_overview = False
            result.append(line)
        else:
            result.append(line)
    
    content = '\n'.join(result)
    
    # 更新最后更新时间
    last_update_line = f"**最后更新**: {build_date}"
    
    if "**最后更新**:" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "**最后更新**:" in line:
                lines[i] = last_update_line
                break
        content = '\n'.join(lines)
    else:
        # 如果没有最后更新行，添加到文档末尾
        content += f"\n\n{last_update_line}"
    
    return content

def main():
    parser = argparse.ArgumentParser(description='更新项目版本信息并管理文档')
    parser.add_argument('--version', help='新版本号 (例如 1.0.1)')
    parser.add_argument('--date', help='构建日期 (默认为今天)')
    parser.add_argument('--clean', action='store_true', help='清理带时间戳的文件')
    parser.add_argument('--migrate', action='store_true', help='迁移带时间戳的文件到单文件系统')
    parser.add_argument('--doc', help='指定要更新的文档文件')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    
    if args.clean:
        print("清理带时间戳的文件...")
        
        file_bases = ['README', 'ARCHITECTURE', 'requirements', 'build']
        total_deleted = 0
        
        for base in file_bases:
            deleted = cleanup_timestamped_files(project_root, base)
            if deleted > 0:
                print(f"- 已删除 {deleted} 个 {base} 文件")
                total_deleted += deleted
        
        print(f"清理完成: 已删除 {total_deleted} 个文件")
    
    if args.migrate:
        print("迁移带时间戳的文件到单文件系统...")
        result = migrate_to_single_file_system(project_root)
        print(f"迁移完成: ")
        print(f"- 迁移的文件: {result['migrated_files']}")
        print(f"- 删除的文件: {result['deleted_files']}")
        print(f"- 错误: {result['errors']}")
    
    if args.version:
        build_date = args.date or datetime.now().strftime("%Y-%m-%d")
        print(f"更新版本信息: {args.version} (构建日期: {build_date})")
        
        # 更新settings.py
        settings_path = project_root / "src" / "config" / "settings.py"
        if update_version_in_file(settings_path, args.version, build_date):
            print(f"- 已更新设置文件")
        
        # 更新VERSION_TRACKER.md
        version_tracker_path = project_root / "docs" / "VERSION_TRACKER.md"
        if update_version_in_file(version_tracker_path, args.version, build_date):
            print(f"- 已更新版本跟踪文件")
        
        # 如果指定了特定文档，优先更新它
        if args.doc:
            doc_path = project_root / "docs" / args.doc
            if not doc_path.exists():
                doc_path = project_root / args.doc
            
            if doc_path.exists() and update_version_in_file(doc_path, args.version, build_date):
                print(f"- 已更新 {args.doc}")
        else:
            # 更新主要文档
            docs = [
                project_root / "README.md",
                project_root / "ARCHITECTURE.md",
                project_root / "docs" / "PROJECT_PLAN.md"
            ]
            
            for doc in docs:
                if doc.exists() and update_version_in_file(doc, args.version, build_date):
                    print(f"- 已更新 {doc.name}")
        
        print("版本更新完成")

if __name__ == "__main__":
    main() 
 