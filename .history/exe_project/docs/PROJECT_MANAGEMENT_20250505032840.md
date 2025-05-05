# 项目管理指南

本文档提供了项目管理和进度跟踪的详细指导，包括如何使用项目计划工具、更新任务状态、生成报告等。**注意：本项目尚处于计划阶段，预计于2025年6月开始实施。**

## 项目基本信息

| 项目名称 | 高级EXE应用程序 |
|---------|---------------|
| 当前状态 | 计划阶段 |
| 计划开始日期 | 2025-06-01 |
| 计划完成日期 | 2025-07-31 |
| 当前版本 | 1.1.0 (2025-05-05) |
| 开发者 | xiangye72 (个人开发者) |
| GitHub | [ch777777](https://github.com/ch777777) |

## 项目计划工具

我们已经准备好以下工具，将在项目实施阶段使用：

1. **项目计划文档** - `docs/PROJECT_PLAN.md` 包含所有项目信息和进度
2. **进度更新工具** - `src/utils/project_plan_updater.py` 用于自动更新项目计划
3. **版本管理工具** - `manage_versions.py` 用于更新版本信息

## 任务状态更新

### 更新任务状态

```bash
# 更新任务状态（completed, in_progress, not_started, cancelled, at_risk）
python src/utils/project_plan_updater.py task <任务ID> <新状态> [--hours <实际工时>] [--date <完成日期>]

# 示例：将任务T4.7标记为进行中
python src/utils/project_plan_updater.py task T4.7 in_progress

# 示例：将任务T4.7标记为已完成，实际花费9小时
python src/utils/project_plan_updater.py task T4.7 completed --hours 9h --date 2024-06-15
```

### 更新里程碑状态

```bash
# 更新里程碑状态
python src/utils/project_plan_updater.py milestone <里程碑ID> <新状态> [--date <实际日期>]

# 示例：将里程碑M4标记为已完成
python src/utils/project_plan_updater.py milestone M4 completed --date 2024-06-10
```

### 更新项目状态

```bash
# 更新项目整体状态
python src/utils/project_plan_updater.py project <新状态>

# 示例：将项目状态更新为"测试中"
python src/utils/project_plan_updater.py project "测试中"
```

## 进度跟踪

### 添加每周进度统计

```bash
# 添加每周进度统计
python src/utils/project_plan_updater.py week <周次> <日期范围> <计划工时> <实际工时> <完成任务> <偏差分析>

# 示例：添加第7周进度
python src/utils/project_plan_updater.py week W7 "2024-08-12~2024-08-18" 18h 20h "T4.6,T4.7" "略有延迟"
```

### 更新进度统计数据

```bash
# 自动重新计算进度统计数据
python src/utils/project_plan_updater.py stats
```

## 风险管理

### 更新风险状态

```bash
# 更新风险状态
python src/utils/project_plan_updater.py risk <风险ID> <新状态>

# 示例：更新风险R1状态
python src/utils/project_plan_updater.py risk R1 "已缓解"
```

## 变更管理

### 添加项目变更记录

```bash
# 添加项目变更记录
python src/utils/project_plan_updater.py change <变更ID> <日期> <变更内容> <原因> <影响分析> <审批人>

# 示例：添加变更记录
python src/utils/project_plan_updater.py change C4 2024-08-15 "调整测试策略" "发现更高效的测试方法" "减少测试工作量约5小时" "张经理"
```

## 后续行动管理

### 更新下一步行动

```bash
# 更新下一步行动列表
python src/utils/project_plan_updater.py actions "行动1" "行动2" "行动3"

# 示例：更新下一步行动
python src/utils/project_plan_updater.py actions "开始模块集成测试" "准备测试计划" "评估当前进度" "更新风险报告"
```

## 版本管理

### 更新版本信息

```bash
# 更新项目版本信息（同时更新项目计划）
python manage_versions.py --version <版本号> --doc PROJECT_PLAN.md

# 示例：更新到版本1.2.0
python manage_versions.py --version 1.2.0 --doc PROJECT_PLAN.md
```

## 项目启动前准备

在项目开始前（2025年6月），应完成以下准备工作：

1. **环境准备** - 确保所有开发环境已配置完成
2. **需求确认** - 对项目需求文档进行最终确认
3. **项目计划确认** - 对项目计划进行最终确认
4. **风险评估** - 进行项目风险评估和应对措施准备

## 项目启动后工作流程

项目启动后将遵循以下工作流程：

1. **每日更新** - 每日工作结束时更新任务状态
2. **周报生成** - 每周五生成周报并更新周进度统计
3. **里程碑审查** - 每个里程碑结束时进行审查
4. **版本更新** - 重要功能完成后更新版本号
5. **变更管理** - 记录所有范围和时间的变更

## 常见问题与解决方案

### 问题1：工具运行出错

如果进度更新工具运行出错，请检查：

1. 确保在项目根目录运行命令
2. 确认PROJECT_PLAN.md文件结构没有被破坏
3. 确认输入的任务ID存在

### 问题2：统计数据不准确

如果进度统计不准确：

1. 手动运行 `python src/utils/project_plan_updater.py stats` 重新计算
2. 检查任务工时格式是否正确（如 5h）
3. 确认任务状态标记正确

### 问题3：文件冲突

如果多人同时编辑项目计划导致冲突：

1. 先解决文件冲突
2. 运行 `python src/utils/project_plan_updater.py stats` 重新计算统计数据
3. 检查变更是否已合并正确

## 项目文档链接

- [项目计划](PROJECT_PLAN.md) - 包含项目目标、里程碑、任务分解和进度统计
- [版本跟踪记录](VERSION_TRACKER.md) - 版本历史和变更记录
- [架构决策记录](DECISION_LOG.md) - 记录重要技术决策
- [功能请求模板](FEATURE_REQUEST_TEMPLATE.md) - 用于提交新功能请求

---

**最后更新**: 2025-05-05 03:26:14  
**更新人**: xiangye72  
**状态**: 计划阶段文档，个人开发项目 