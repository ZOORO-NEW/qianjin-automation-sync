# qianjin-automation-sync

WorkBuddy 自动化任务跨设备备份、导出、导入与迁移工具。

## Problem

WorkBuddy 的自动化任务存储在本地 SQLite 数据库 (`~/.workbuddy/workbuddy.db`) 中，不支持跨设备云同步。换电脑后自动化任务不会自动出现。

## Solution

此 Skill 通过 `automation_update` 工具的官方 API（list / view / create）实现：

- **导出**：将所有自动化任务配置序列化为标准 JSON 文件
- **导入**：从 JSON 文件重建所有自动化任务
- **安全**：导出前扫描敏感信息（API Key、密码、私钥等），支持脱敏
- **兼容**：导入时检测设备路径，提示用户修正

不直接操作 SQLite 数据库，避免数据库损坏风险。

## Install

### 方法一：直接克隆

```bash
git clone https://github.com/ZOORO-NEW/qianjin-automation-sync.git
cp -r qianjin-automation-sync ~/.workbuddy/skills/automation-sync
```

### 方法二：手动安装

1. 下载此仓库的 ZIP 包
2. 解压后将 `automation-sync` 文件夹放到 `~/.workbuddy/skills/`

安装后对 WorkBuddy 说"导出自动化"或"备份自动化"即可触发。

## Usage

### 导出

```
用户：导出自动化任务
WorkBuddy：（列出所有任务，扫描敏感信息，生成 JSON 文件）
```

### 导入

```
用户：导入自动化任务，文件路径是 xxx.json
WorkBuddy：（读取 JSON，幂等检查，逐条创建，报告结果）
```

## JSON Format

```json
{
  "metadata": {
    "version": "1.0",
    "exported_at": "2026-07-07T12:30:00+08:00",
    "total_count": 2,
    "source_device": "PC-001"
  },
  "automations": [
    {
      "name": "每日任务",
      "prompt": "...",
      "status": "ACTIVE",
      "scheduleType": "recurring",
      "rrule": "FREQ=DAILY;BYHOUR=9;BYMINUTE=0",
      "cwds": "/path/to/workspace"
    }
  ]
}
```

## File Structure

```
automation-sync/
├── SKILL.md                       # Skill 主文件（流程定义 + JSON规范）
├── references/
│   └── security-scan.md           # 敏感信息扫描规则
└── scripts/
    └── test_export_import.py      # 测试脚本
```

## Requirements

- WorkBuddy 桌面版
- `automation_update` 工具（WorkBuddy 内置）

## License

MIT
