"""
项目计划更新工具
提供自动更新项目计划文档的功能，支持任务状态更新和进度跟踪
"""
import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加上级目录到路径，确保正确导入
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入文件管理工具
try:
    from src.utils.file_manager import update_document
except ImportError:
    # 如果从命令行直接运行，使用相对导入
    from .file_manager import update_document

# 任务状态常量
TASK_STATUS = {
    "completed": "✅ 已完成",
    "in_progress": "🔄 进行中",
    "not_started": "⏳ 未开始",
    "cancelled": "❌ 已取消",
    "at_risk": "⚠️ 有风险"
}

def update_task_status(plan_content, task_id, new_status, actual_hours=None, completion_date=None):
    """
    更新项目计划中任务的状态
    
    Args:
        plan_content (str): 项目计划内容
        task_id (str): 任务ID (例如 T1.1, T2.3)
        new_status (str): 新状态 (completed, in_progress, not_started, cancelled, at_risk)
        actual_hours (str, optional): 实际工时 (例如 5h)
        completion_date (str, optional): 完成日期 (格式: YYYY-MM-DD)
    
    Returns:
        str: 更新后的内容
    """
    if new_status not in TASK_STATUS:
        raise ValueError(f"无效的任务状态: {new_status}。有效值: {', '.join(TASK_STATUS.keys())}")
    
    # 如果状态是已完成，但没有提供完成日期，使用当前日期
    if new_status == "completed" and not completion_date:
        completion_date = datetime.now().strftime("%Y-%m-%d")
    
    lines = plan_content.split('\n')
    result = []
    task_found = False
    
    # 查找并更新任务行
    for line in lines:
        if f"| {task_id} |" in line:
            parts = line.split('|')
            if len(parts) >= 7:  # 确保任务行有足够的列
                # 更新状态（通常是第5列）
                parts[5] = f" {TASK_STATUS[new_status]} "
                
                # 如果提供了实际工时，更新实际工时列（第4列）
                if actual_hours:
                    parts[4] = f" {actual_hours} "
                
                # 如果已完成，更新完成日期（第7列）
                if completion_date:
                    parts[7] = f" {completion_date} "
                elif new_status != "completed":
                    # 如果状态不是已完成，清空完成日期
                    parts[7] = " - "
                
                task_found = True
                result.append('|'.join(parts))
            else:
                result.append(line)
        else:
            result.append(line)
    
    if not task_found:
        raise ValueError(f"未找到任务ID: {task_id}")
    
    # 更新最后更新时间
    content = '\n'.join(result)
    last_update_line = f"**最后更新**: {datetime.now().strftime('%Y-%m-%d')}"
    
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
    
    # 更新更新人
    update_by_line = f"**更新人**: {os.environ.get('USERNAME', '未知用户')}"
    
    if "**更新人**:" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "**更新人**:" in line:
                lines[i] = update_by_line
                break
        content = '\n'.join(lines)
    
    return content

def update_milestone_status(plan_content, milestone_id, new_status, actual_date=None):
    """
    更新项目计划中里程碑的状态
    
    Args:
        plan_content (str): 项目计划内容
        milestone_id (str): 里程碑ID (例如 M1, M2)
        new_status (str): 新状态 (completed, in_progress, not_started, cancelled, at_risk)
        actual_date (str, optional): 实际完成日期 (格式: YYYY-MM-DD)
    
    Returns:
        str: 更新后的内容
    """
    if new_status not in TASK_STATUS:
        raise ValueError(f"无效的任务状态: {new_status}。有效值: {', '.join(TASK_STATUS.keys())}")
    
    # 如果状态是已完成，但没有提供实际日期，使用当前日期
    if new_status == "completed" and not actual_date:
        actual_date = datetime.now().strftime("%Y-%m-%d")
    
    lines = plan_content.split('\n')
    result = []
    milestone_found = False
    
    # 查找并更新里程碑行
    for line in lines:
        if f"| {milestone_id} |" in line and "里程碑" in line:
            parts = line.split('|')
            if len(parts) >= 6:  # 确保里程碑行有足够的列
                # 更新状态（通常是第5列）
                parts[5] = f" {TASK_STATUS[new_status]} "
                
                # 如果提供了实际日期，更新实际日期列（第4列）
                if actual_date:
                    parts[4] = f" {actual_date} "
                elif new_status != "completed":
                    # 如果状态不是已完成，清空实际日期
                    parts[4] = " - "
                
                milestone_found = True
                result.append('|'.join(parts))
            else:
                result.append(line)
        else:
            result.append(line)
    
    if not milestone_found:
        raise ValueError(f"未找到里程碑ID: {milestone_id}")
    
    # 更新最后更新时间
    content = '\n'.join(result)
    today = datetime.now().strftime("%Y-%m-%d")
    last_update_line = f"**最后更新**: {today}"
    
    if "**最后更新**:" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "**最后更新**:" in line:
                lines[i] = last_update_line
                break
        content = '\n'.join(lines)
    
    # 更新更新人
    update_by_line = f"**更新人**: {os.environ.get('USERNAME', '未知用户')}"
    
    if "**更新人**:" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "**更新人**:" in line:
                lines[i] = update_by_line
                break
        content = '\n'.join(lines)
    
    return content

def update_project_status(plan_content, project_status):
    """
    更新项目状态
    
    Args:
        plan_content (str): 项目计划内容
        project_status (str): 新的项目状态
    
    Returns:
        str: 更新后的内容
    """
    lines = plan_content.split('\n')
    result = []
    
    # 查找并更新项目状态行
    for line in lines:
        if "| 项目状态 |" in line:
            parts = line.split('|')
            if len(parts) >= 3:
                parts[2] = f" {project_status} "
                result.append('|'.join(parts))
            else:
                result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def update_progress_statistics(plan_content):
    """
    更新项目进度统计
    
    Args:
        plan_content (str): 项目计划内容
    
    Returns:
        str: 更新后的内容
    """
    # 解析所有任务以计算统计信息
    total_planned_hours = 0
    total_actual_hours = 0
    completed_tasks = 0
    total_tasks = 0
    
    pattern = r"\|\s*T\d+\.\d+\s*\|\s*[^|]+\|\s*(\d+)h\s*\|\s*([^|]*)\|\s*([^|]*)\|"
    
    matches = re.findall(pattern, plan_content)
    for match in matches:
        planned_hours = int(match[0])
        actual_hours_str = match[1].strip()
        status = match[2].strip()
        
        total_planned_hours += planned_hours
        total_tasks += 1
        
        if "已完成" in status:
            completed_tasks += 1
            # 提取实际工时
            if actual_hours_str and 'h' in actual_hours_str:
                try:
                    actual_hours = int(actual_hours_str.replace('h', '').strip())
                    total_actual_hours += actual_hours
                except ValueError:
                    # 如果无法解析为数字，使用计划工时
                    total_actual_hours += planned_hours
        
    # 计算剩余工时和进度百分比
    completed_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    # 查找并更新统计部分
    lines = plan_content.split('\n')
    result = []
    in_stats_section = False
    stats_updated = False
    
    for line in lines:
        if "### 总体进度" in line:
            in_stats_section = True
            result.append(line)
        elif in_stats_section and line.startswith('- '):
            if "计划总工时:" in line:
                result.append(f"- 计划总工时: {total_planned_hours}小时")
            elif "已完成工时:" in line:
                result.append(f"- 已完成工时: {total_actual_hours}小时")
            elif "剩余工时:" in line:
                result.append(f"- 剩余工时: {total_planned_hours - total_actual_hours}小时")
            elif "当前进度:" in line:
                result.append(f"- 当前进度: {completed_percentage}%")
            else:
                result.append(line)
        elif in_stats_section and line.startswith('##'):
            # 下一个主要章节开始
            in_stats_section = False
            result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def add_weekly_progress(plan_content, week_number, date_range, planned_hours, actual_hours, completed_tasks, deviation_analysis):
    """
    添加每周进度统计
    
    Args:
        plan_content (str): 项目计划内容
        week_number (str): 周次 (例如 W7)
        date_range (str): 日期范围 (例如 2024-06-10 ~ 2024-06-16)
        planned_hours (str): 计划完成工时 (例如 20h)
        actual_hours (str): 实际完成工时 (例如 18h)
        completed_tasks (str): 完成任务列表 (例如 T4.6, T4.7)
        deviation_analysis (str): 偏差分析 (例如 符合计划)
    
    Returns:
        str: 更新后的内容
    """
    lines = plan_content.split('\n')
    result = []
    weekly_table_found = False
    weekly_table_end_index = -1
    
    # 查找每周进度统计表格
    for i, line in enumerate(lines):
        if "| 周次 | 日期范围 | 计划完成工时 | 实际完成工时 | 完成任务 | 偏差分析 |" in line:
            weekly_table_found = True
        elif weekly_table_found and line.strip() == "" and i > 0:
            # 找到表格结束位置
            weekly_table_end_index = i
            break
    
    if weekly_table_found and weekly_table_end_index > 0:
        # 检查是否已存在相同周次
        week_exists = False
        for line in lines:
            if f"| {week_number} |" in line:
                week_exists = True
                break
        
        # 如果周次不存在，添加新行
        if not week_exists:
            # 在表格末尾添加新行
            new_week_line = f"| {week_number} | {date_range} | {planned_hours} | {actual_hours} | {completed_tasks} | {deviation_analysis} |"
            
            # 构建结果
            result = lines[:weekly_table_end_index]
            result.append(new_week_line)
            result.extend(lines[weekly_table_end_index:])
        else:
            # 更新现有周次行
            for i, line in enumerate(lines):
                if f"| {week_number} |" in line:
                    lines[i] = f"| {week_number} | {date_range} | {planned_hours} | {actual_hours} | {completed_tasks} | {deviation_analysis} |"
            result = lines
    else:
        # 表格未找到，不做更改
        result = lines
    
    return '\n'.join(result)

def update_risk_status(plan_content, risk_id, status):
    """
    更新风险状态
    
    Args:
        plan_content (str): 项目计划内容
        risk_id (str): 风险ID (例如 R1)
        status (str): 新状态
    
    Returns:
        str: 更新后的内容
    """
    lines = plan_content.split('\n')
    result = []
    risk_found = False
    
    # 查找并更新风险行
    for line in lines:
        if f"| {risk_id} |" in line:
            parts = line.split('|')
            if len(parts) >= 7:  # 确保风险行有足够的列
                # 更新状态（最后一列）
                parts[6] = f" {status} "
                risk_found = True
                result.append('|'.join(parts))
            else:
                result.append(line)
        else:
            result.append(line)
    
    if not risk_found:
        raise ValueError(f"未找到风险ID: {risk_id}")
    
    return '\n'.join(result)

def add_project_change(plan_content, change_id, date, content, reason, impact, approver):
    """
    添加项目变更记录
    
    Args:
        plan_content (str): 项目计划内容
        change_id (str): 变更ID (例如 C4)
        date (str): 变更日期 (格式: YYYY-MM-DD)
        content (str): 变更内容
        reason (str): 变更原因
        impact (str): 影响分析
        approver (str): 审批人
    
    Returns:
        str: 更新后的内容
    """
    lines = plan_content.split('\n')
    result = []
    changes_table_found = False
    changes_table_end_index = -1
    
    # 查找项目变更记录表格
    for i, line in enumerate(lines):
        if "| ID | 日期 | 变更内容 | 原因 | 影响分析 | 审批人 |" in line:
            changes_table_found = True
        elif changes_table_found and line.strip() == "" and i > 0:
            # 找到表格结束位置
            changes_table_end_index = i
            break
    
    if changes_table_found and changes_table_end_index > 0:
        # 检查是否已存在相同变更ID
        change_exists = False
        for line in lines:
            if f"| {change_id} |" in line:
                change_exists = True
                break
        
        # 如果变更ID不存在，添加新行
        if not change_exists:
            # 在表格末尾添加新行
            new_change_line = f"| {change_id} | {date} | {content} | {reason} | {impact} | {approver} |"
            
            # 构建结果
            result = lines[:changes_table_end_index]
            result.append(new_change_line)
            result.extend(lines[changes_table_end_index:])
        else:
            # 更新现有变更行
            for i, line in enumerate(lines):
                if f"| {change_id} |" in line:
                    lines[i] = f"| {change_id} | {date} | {content} | {reason} | {impact} | {approver} |"
            result = lines
    else:
        # 表格未找到，不做更改
        result = lines
    
    return '\n'.join(result)

def update_next_actions(plan_content, next_actions):
    """
    更新下一步行动
    
    Args:
        plan_content (str): 项目计划内容
        next_actions (list): 下一步行动列表
    
    Returns:
        str: 更新后的内容
    """
    lines = plan_content.split('\n')
    result = []
    next_actions_section_found = False
    next_actions_section_start = -1
    next_actions_section_end = -1
    
    # 查找"下一步行动"部分
    for i, line in enumerate(lines):
        if "## 下一步行动" in line:
            next_actions_section_found = True
            next_actions_section_start = i + 1
        elif next_actions_section_found and line.startswith('##'):
            # 找到下一个章节
            next_actions_section_end = i
            break
    
    # 如果没有找到下一个章节，可能"下一步行动"是最后一节
    if next_actions_section_found and next_actions_section_end == -1:
        # 找到分隔线或文档结束
        for i in range(next_actions_section_start, len(lines)):
            if lines[i].startswith('---') or i == len(lines) - 1:
                next_actions_section_end = i
                break
    
    if next_actions_section_found and next_actions_section_start > 0 and next_actions_section_end > next_actions_section_start:
        # 构建新的"下一步行动"部分
        next_actions_lines = [f"{i+1}. {action}" for i, action in enumerate(next_actions)]
        
        # 构建结果
        result = lines[:next_actions_section_start]
        result.extend(next_actions_lines)
        result.extend([''])  # 添加一个空行
        result.extend(lines[next_actions_section_end:])
    else:
        # 部分未找到，不做更改
        result = lines
    
    return '\n'.join(result)

def main():
    parser = argparse.ArgumentParser(description='更新项目计划文档')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 更新任务状态命令
    task_parser = subparsers.add_parser('task', help='更新任务状态')
    task_parser.add_argument('task_id', help='任务ID (例如 T1.1, T2.3)')
    task_parser.add_argument('status', choices=list(TASK_STATUS.keys()), help='新状态')
    task_parser.add_argument('--hours', help='实际工时 (例如 5h)')
    task_parser.add_argument('--date', help='完成日期 (格式: YYYY-MM-DD)')
    
    # 更新里程碑状态命令
    milestone_parser = subparsers.add_parser('milestone', help='更新里程碑状态')
    milestone_parser.add_argument('milestone_id', help='里程碑ID (例如 M1, M2)')
    milestone_parser.add_argument('status', choices=list(TASK_STATUS.keys()), help='新状态')
    milestone_parser.add_argument('--date', help='实际完成日期 (格式: YYYY-MM-DD)')
    
    # 更新项目状态命令
    project_parser = subparsers.add_parser('project', help='更新项目状态')
    project_parser.add_argument('status', help='新的项目状态')
    
    # 添加每周进度命令
    week_parser = subparsers.add_parser('week', help='添加每周进度统计')
    week_parser.add_argument('week_number', help='周次 (例如 W7)')
    week_parser.add_argument('date_range', help='日期范围 (例如 2024-06-10~2024-06-16)')
    week_parser.add_argument('planned_hours', help='计划完成工时 (例如 20h)')
    week_parser.add_argument('actual_hours', help='实际完成工时 (例如 18h)')
    week_parser.add_argument('completed_tasks', help='完成任务列表 (例如 "T4.6, T4.7")')
    week_parser.add_argument('deviation_analysis', help='偏差分析 (例如 "符合计划")')
    
    # 更新风险状态命令
    risk_parser = subparsers.add_parser('risk', help='更新风险状态')
    risk_parser.add_argument('risk_id', help='风险ID (例如 R1)')
    risk_parser.add_argument('status', help='新状态')
    
    # 添加项目变更记录命令
    change_parser = subparsers.add_parser('change', help='添加项目变更记录')
    change_parser.add_argument('change_id', help='变更ID (例如 C4)')
    change_parser.add_argument('date', help='变更日期 (格式: YYYY-MM-DD)')
    change_parser.add_argument('content', help='变更内容')
    change_parser.add_argument('reason', help='变更原因')
    change_parser.add_argument('impact', help='影响分析')
    change_parser.add_argument('approver', help='审批人')
    
    # 更新下一步行动命令
    actions_parser = subparsers.add_parser('actions', help='更新下一步行动')
    actions_parser.add_argument('actions', nargs='+', help='下一步行动列表')
    
    # 更新进度统计命令
    stats_parser = subparsers.add_parser('stats', help='更新进度统计')
    
    # 公共参数
    parser.add_argument('--file', default='docs/PROJECT_PLAN.md', help='项目计划文件路径 (默认: docs/PROJECT_PLAN.md)')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    plan_file = project_root / args.file
    
    if not plan_file.exists():
        print(f"错误: 项目计划文件不存在 - {plan_file}")
        return 1
    
    try:
        # 读取项目计划文件
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_content = f.read()
        
        # 根据命令更新内容
        if args.command == 'task':
            plan_content = update_task_status(plan_content, args.task_id, args.status, args.hours, args.date)
            print(f"已更新任务 {args.task_id} 状态为 {TASK_STATUS[args.status]}")
        
        elif args.command == 'milestone':
            plan_content = update_milestone_status(plan_content, args.milestone_id, args.status, args.date)
            print(f"已更新里程碑 {args.milestone_id} 状态为 {TASK_STATUS[args.status]}")
        
        elif args.command == 'project':
            plan_content = update_project_status(plan_content, args.status)
            print(f"已更新项目状态为 {args.status}")
        
        elif args.command == 'week':
            plan_content = add_weekly_progress(
                plan_content, 
                args.week_number,
                args.date_range,
                args.planned_hours,
                args.actual_hours,
                args.completed_tasks,
                args.deviation_analysis
            )
            print(f"已添加/更新 {args.week_number} 周进度统计")
        
        elif args.command == 'risk':
            plan_content = update_risk_status(plan_content, args.risk_id, args.status)
            print(f"已更新风险 {args.risk_id} 状态为 {args.status}")
        
        elif args.command == 'change':
            plan_content = add_project_change(
                plan_content,
                args.change_id,
                args.date,
                args.content,
                args.reason,
                args.impact,
                args.approver
            )
            print(f"已添加/更新变更记录 {args.change_id}")
        
        elif args.command == 'actions':
            plan_content = update_next_actions(plan_content, args.actions)
            print("已更新下一步行动")
        
        elif args.command == 'stats':
            plan_content = update_progress_statistics(plan_content)
            print("已更新进度统计")
        
        else:
            print("错误: 未指定命令。使用 -h 查看帮助。")
            return 1
        
        # 总是更新进度统计
        if args.command != 'stats':
            plan_content = update_progress_statistics(plan_content)
        
        # 写入更新后的内容
        update_document(plan_file, plan_content)
        
        return 0
    
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
 