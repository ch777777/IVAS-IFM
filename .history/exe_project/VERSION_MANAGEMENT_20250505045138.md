# IFMCM 版本管理说明 (版本 1.1.0 - 2025-05-05)
# Information Flow Material Centralized Management

## 版本管理概述

IFMCM(信息流素材集中管理系统)采用内置的版本管理系统，通过单一文件实时更新版本信息，避免创建多个时间戳文件。该系统用于跟踪应用程序版本并保持文档一致性。

## 功能概述

1. **实时文件更新** - 在同一个文件中更新内容，而不是创建新的带时间戳的文件
2. **版本跟踪** - 在文档中维护版本信息，并在`VERSION_TRACKER.md`中集中管理所有版本历史
3. **备份机制** - 在更新文件前创建备份，便于恢复
4. **时间戳文件清理** - 自动清理工作区中的带时间戳文件

## 工具及其用途

### 主要工具

1. **`manage_versions.py`** - 项目根目录中的主要版本管理脚本
2. **`cleanup_workspace.py`** - 工作区清理脚本（在上级目录）

### 核心模块

1. **`src/utils/file_manager.py`** - 提供文件操作和版本管理的核心功能
2. **`src/utils/update_version.py`** - 实现版本更新逻辑

## 使用方法

### 更新版本号

要更新项目的版本号，请运行：

```
python manage_versions.py --version 1.0.1
```

这将：
- 更新`src/config/settings.py`中的版本信息
- 更新`docs/VERSION_TRACKER.md`中的版本历史
- 在`README.md`和`ARCHITECTURE.md`中更新版本信息

### 指定构建日期

如果需要指定构建日期（默认为当天），可以使用：

```
python manage_versions.py --version 1.0.1 --date 2024-05-10
```

### 清理带时间戳的文件

要清理项目中的带时间戳文件：

```
python manage_versions.py --clean
```

### 迁移到单文件系统

如果工作区中存在大量带时间戳的文件，可以使用迁移工具：

```
python manage_versions.py --migrate
```

这将自动：
1. 查找所有带时间戳的文件
2. 对于每种文件类型，保留最新版本并更新到标准文件名
3. 删除所有时间戳文件

### 清理整个工作区

要清理整个工作区（包括项目外的文件），请在上级目录运行：

```
python cleanup_workspace.py
```

如果希望先查看将执行的操作而不实际执行，可以使用：

```
python cleanup_workspace.py --dry-run
```

### 打包时更新版本

构建脚本已更新，支持在打包时指定新版本：

```
build.bat --version 1.0.1
```

## 版本信息存储

版本信息存储在以下位置：

1. **主要版本信息** - `src/config/settings.py`中的`VERSION`和`BUILD_DATE`变量
2. **版本历史** - `docs/VERSION_TRACKER.md`文件
3. **文档版本标记** - 在主要文档（如`README.md`和`ARCHITECTURE.md`）的标题中

## 备份机制

文件更新时会自动创建备份：

1. 备份存储在原文件目录的`backups`子目录中
2. 备份文件名包含时间戳，确保多次更新不会覆盖
3. 默认情况下总是创建备份，可以通过API禁用

## 开发指南

### 添加新文件类型支持

如果要添加新的文件类型到版本管理系统，请修改`src/utils/update_version.py`中的`main`函数：

```python
docs = [
    project_root / "README.md",
    project_root / "ARCHITECTURE.md",
    # 在此添加新文件路径
]
```

### 自定义版本格式

如果需要更改版本信息的格式，请修改`src/utils/file_manager.py`中的`add_version_to_document`函数。

## 最佳实践

1. **经常更新版本** - 在完成重要功能或修复后更新版本号
2. **遵循版本号规范** - 使用语义化版本号(X.Y.Z)，X为主版本，Y为次版本，Z为补丁版本
3. **保持文档同步** - 确保VERSION_TRACKER.md文件中的更新记录与实际更改同步
4. **不要手动编辑时间戳文件** - 始终使用提供的工具来管理文件版本 
 