# 项目提问与文档索引

本目录包含项目开发过程中的提问模板、决策记录和实施指南，用于指导项目各阶段的系统化开发。

## 项目规划与需求收集

### [项目需求与设计提问清单](PROJECT_QUESTIONNAIRE.md)
在项目启动阶段使用该问卷收集关键信息，明确项目范围、目标和约束条件。此问卷应由产品负责人、开发团队和关键利益相关者共同完成。

### [功能请求模板](FEATURE_REQUEST_TEMPLATE.md)
用于规范地描述和记录单个功能需求。每个新功能应使用此模板创建一个功能请求文档，确保需求描述完整、明确。

## 设计与决策

### [架构决策记录](DECISION_LOG.md)
记录项目中的重要架构和技术决策，包括决策背景、考虑的选项、最终选择及其理由。所有重大技术决策都应记录在此。

### [模块设计文档模板](MODULE_DESIGN_TEMPLATE.md)
在开始实现特定模块前，使用此模板创建详细的模块设计文档。包括模块目标、接口、数据结构和实现考量等。

## 实施检查清单

### [模块实现前检查清单](IMPLEMENTATION_CHECKLIST.md)
在开始编码前使用此清单确保所有必要的设计决策已经作出，需求已充分理解，实施准备工作已完成。

### [代码审查检查清单](CODE_REVIEW_CHECKLIST.md)
代码审查过程中使用此清单，确保代码质量、功能正确性、安全性和维护性等方面得到全面检查。

## 如何使用这些文档

1. **项目启动阶段**:
   - 填写 [项目需求与设计提问清单](PROJECT_QUESTIONNAIRE.md)
   - 创建初始 [架构决策记录](DECISION_LOG.md)

2. **需求分析阶段**:
   - 为每个功能使用 [功能请求模板](FEATURE_REQUEST_TEMPLATE.md)
   - 对关键功能进行优先级排序和依赖分析

3. **设计阶段**:
   - 使用 [模块设计文档模板](MODULE_DESIGN_TEMPLATE.md) 设计各模块
   - 更新 [架构决策记录](DECISION_LOG.md) 记录设计决策

4. **实施前准备**:
   - 使用 [模块实现前检查清单](IMPLEMENTATION_CHECKLIST.md) 确保准备就绪
   - 明确开发任务和优先级

5. **开发与审查阶段**:
   - 按模块设计文档实施功能
   - 使用 [代码审查检查清单](CODE_REVIEW_CHECKLIST.md) 进行代码审查

## 文档维护指南

- 所有文档应保持更新，反映当前项目状态
- 重大变更应记录在相应文档的修订历史中
- 文档应作为代码库的一部分进行版本控制
- 鼓励团队成员提出改进文档模板的建议

---

通过系统化的提问和文档管理流程，我们可以确保项目开发的各个阶段都有清晰的指导，减少误解和返工，提高开发效率和代码质量。

# 项目文档索引

本文档提供项目所有文档的导航和概述，帮助团队成员快速找到所需信息。

## 核心文档

| 文档名称 | 路径 | 描述 | 适用对象 |
|---------|------|------|---------|
| [README](../README.md) | `/README.md` | 项目概览、结构和使用说明 | 所有人 |
| [架构设计](../ARCHITECTURE.md) | `/ARCHITECTURE.md` | 项目架构和设计决策 | 开发人员 |
| [项目计划](PROJECT_PLAN.md) | `/docs/PROJECT_PLAN.md` | 项目进度计划和实时跟踪 | 项目管理、开发人员 |
| [版本管理说明](../VERSION_MANAGEMENT.md) | `/VERSION_MANAGEMENT.md` | 版本管理系统使用指南 | 开发人员 |
| [版本跟踪记录](VERSION_TRACKER.md) | `/docs/VERSION_TRACKER.md` | 详细版本历史和变更记录 | 所有人 |

## 开发流程文档

| 文档名称 | 路径 | 描述 | 适用对象 |
|---------|------|------|---------|
| [项目需求问卷](PROJECT_QUESTIONNAIRE.md) | `/docs/PROJECT_QUESTIONNAIRE.md` | 收集项目需求的结构化问题 | 需求分析人员 |
| [功能请求模板](FEATURE_REQUEST_TEMPLATE.md) | `/docs/FEATURE_REQUEST_TEMPLATE.md` | 新功能请求的标准格式 | 产品经理、用户 |
| [架构决策记录](DECISION_LOG.md) | `/docs/DECISION_LOG.md` | 重要技术决策及其理由 | 架构师、开发人员 |
| [模块设计模板](MODULE_DESIGN_TEMPLATE.md) | `/docs/MODULE_DESIGN_TEMPLATE.md` | 模块详细设计文档模板 | 开发人员 |
| [实现前检查清单](IMPLEMENTATION_CHECKLIST.md) | `/docs/IMPLEMENTATION_CHECKLIST.md` | 开发前的准备工作检查 | 开发人员 |
| [代码审查检查清单](CODE_REVIEW_CHECKLIST.md) | `/docs/CODE_REVIEW_CHECKLIST.md` | 代码审查标准和流程 | 审查者、开发人员 |

## 技术文档

| 文档名称 | 路径 | 描述 | 适用对象 |
|---------|------|------|---------|
| [配置模块](../src/config/settings.py) | `/src/config/settings.py` | 应用程序配置常量 | 开发人员 |
| [工具函数模块](../src/utils/helpers.py) | `/src/utils/helpers.py` | 通用工具函数实现 | 开发人员 |
| [UI组件模块](../src/components/ui_components.py) | `/src/components/ui_components.py` | 自定义UI组件实现 | 开发人员、UI设计师 |
| [主应用程序类](../src/components/app.py) | `/src/components/app.py` | 应用程序主类实现 | 开发人员 |
| [文件管理工具](../src/utils/file_manager.py) | `/src/utils/file_manager.py` | 版本管理和文件操作工具 | 开发人员 |
| [版本更新工具](../src/utils/update_version.py) | `/src/utils/update_version.py` | 版本更新实现逻辑 | 开发人员 |

## 如何使用这些文档

1. **新加入项目**：从 README 开始，然后查看架构设计文档，最后阅读项目计划了解当前状态
2. **理解设计决策**：查看架构决策记录了解重要设计选择的原因
3. **开发新功能**：先填写功能请求模板，然后使用模块设计模板设计实现方案
4. **实现前准备**：使用实现前检查清单确保开发准备就绪
5. **代码审查**：使用代码审查检查清单确保代码质量
6. **版本管理**：参考版本管理说明进行版本更新和发布

## 文档维护

所有文档应定期更新以保持与代码一致。文档更新应遵循以下原则：

1. 代码变更时相关文档必须同步更新
2. 使用版本管理工具跟踪文档版本变化
3. 定期审查文档确保准确性和完整性
4. 文档改进建议应通过功能请求提出

上次更新: 2024-06-06 
 
 