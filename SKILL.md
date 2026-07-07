---
name: automation-sync
description: "WorkBuddy 自动化任务的跨设备备份、导出、导入与迁移工具。当用户需要备份自动化任务、导出自动化配置、迁移自动化到新设备、跨电脑同步自动化任务时使用此技能。触发词包括：导出自动化、备份自动化、导入自动化、迁移自动化、同步自动化任务、automation export/import/backup/restore/sync/migrate、换电脑自动化任务没了、自动化任务跨设备、automation backup。此技能通过 automation_update 工具的 list/view/create 模式实现，不直接操作 SQLite 数据库，确保操作安全可靠。"
agent_created: true
---

# Automation Sync

## Overview

WorkBuddy 的自动化任务存储在本地 SQLite 数据库 (`~/.workbuddy/workbuddy.db`) 中，
不支持跨设备云同步。此技能提供标准化的导出/导入流程，将自动化任务配置序列化为
JSON 文件，用户可通过网盘、U 盘或任何文件传输方式实现跨设备迁移。

## When to Use

- 用户需要备份当前所有自动化任务
- 用户需要将自动化任务迁移到新设备
- 用户换了电脑发现自动化任务丢失，需要从备份恢复
- 用户需要查看或审计所有自动化任务的完整配置
- 用户说"导出自动化""备份自动化""迁移自动化""同步自动化"等

## Export Workflow (导出)

### Step 1: 获取所有自动化任务列表

调用 `automation_update` 工具，`mode="list"`，获取所有自动化任务的摘要列表
（包含 id、name、status、scheduleType、rrule）。

### Step 2: 逐条获取完整配置

对列表中的每个任务，调用 `automation_update` 工具，`mode="view"`，传入对应的 `id`，
获取完整配置。需要提取以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 任务名称（必填） |
| prompt | string | 任务指令（必填） |
| status | string | ACTIVE 或 PAUSED |
| scheduleType | string | recurring 或 once |
| rrule | string | RFC 5545 重复规则（recurring 时必填） |
| scheduledAt | string\|null | 一次性执行时间（once 时必填） |
| validFrom | string\|null | 有效期开始 |
| validUntil | string\|null | 有效期结束 |
| cwds | string\|null | 工作目录（逗号分隔） |
| expertId | string\|null | 专家 ID |
| modelId | string\|null | 模型 ID |
| modelIsThinking | boolean\|null | 是否启用思考模式 |
| connectorIds | array\|null | MCP 连接器 ID 列表 |

### Step 3: 敏感信息扫描

对每条任务的 `prompt` 字段执行敏感信息扫描，检测以下模式：

- API Key: `sk-`、`ak_`、`AKID` 开头的字符串
- Bearer Token: `Bearer ` 后跟长字符串
- 密码赋值: `password=`、`passwd=`、`pwd=` 后跟值
- 私钥: `-----BEGIN` 开头的多行文本
- 连接字符串中的凭证: `://user:pass@` 模式

如果检测到敏感信息，在导出前向用户发出警告，并提供两个选项：
1. 脱敏导出（将敏感部分替换为 `***REDACTED***`）
2. 原样导出（用户确认风险后继续）

### Step 4: 组装 JSON 并写入文件

将所有任务配置组装为标准 JSON 格式（格式规范见下文），使用 Write 工具写入文件。

默认输出路径：当前工作目录下的 `automation-export-{日期}.json`。
用户可指定自定义路径。

### Step 5: 输出摘要

导出完成后，向用户展示：
- 导出文件路径
- 任务总数
- 每条任务的名称和状态
- 敏感信息扫描结果（如有）
- 设备路径提示（见 Security & Compatibility Notes）

## Import Workflow (导入)

### Step 1: 读取 JSON 文件

使用 Read 工具读取用户指定的 JSON 文件路径。验证 JSON 格式合法性，
检查 `metadata.version` 字段是否兼容。

### Step 2: 获取当前已有任务列表

调用 `automation_update`，`mode="list"`，获取当前设备上已有的自动化任务，
用于幂等检查（按 `name` 字段匹配）。

### Step 3: 幂等导入

遍历 JSON 中的每条任务配置：

1. 检查 `name` 是否与现有任务重名
2. 如果重名，向用户询问处理方式：
   - 跳过（保留现有任务）
   - 创建副本（在名称后追加 `_imported_{时间戳}`）
3. 如果不重名，调用 `automation_update`，`mode="create"`，传入所有字段创建任务

### Step 4: 设备路径检查

对每条任务的 `cwds` 和 `prompt` 中的文件路径进行检查：
- 如果路径指向的目录在当前设备上不存在，向用户发出警告
- 提示用户手动修正路径

### Step 5: 输出导入报告

导入完成后，向用户展示：
- 成功导入数量
- 跳过数量及原因
- 失败数量及错误信息
- 需要手动修正路径的任务列表

## JSON Format Specification

```json
{
  "metadata": {
    "version": "1.0",
    "exported_at": "2026-07-07T12:30:00+08:00",
    "total_count": 2,
    "source_device": "用户设备名（可选）"
  },
  "automations": [
    {
      "name": "任务名称",
      "prompt": "任务指令内容",
      "status": "ACTIVE",
      "scheduleType": "recurring",
      "rrule": "FREQ=DAILY;BYHOUR=9;BYMINUTE=0",
      "scheduledAt": null,
      "validFrom": null,
      "validUntil": null,
      "cwds": "C:\\Users\\username\\workdir",
      "expertId": null,
      "modelId": null,
      "modelIsThinking": null,
      "connectorIds": null
    }
  ]
}
```

### Field Rules

- `metadata.version`: 格式版本号，当前为 `1.0`
- `metadata.exported_at`: ISO 8601 格式时间戳
- `metadata.total_count`: 自动化任务数组长度
- `automations[]`: 自动化任务数组，每条包含完整配置
- `null` 值字段在导入时省略，使用 automation_update 的默认行为
- `id` 字段不导出，导入时由系统自动生成新 ID

## Security & Compatibility Notes

### 敏感信息

自动化任务的 `prompt` 字段可能包含 API Key、密码、文件路径等敏感信息。
导出前务必执行敏感信息扫描。JSON 文件应存储在安全位置，避免公开共享。

### 设备路径兼容性

以下字段可能包含设备特定路径，跨设备迁移时需要手动修正：

| 字段 | 路径示例 | 说明 |
|------|----------|------|
| cwds | `C:\Users\ZQJ\WorkBuddy\...` | 工作目录路径 |
| prompt | `C:\Users\ZQJ\...\输出目录\` | prompt 中引用的文件路径 |
| prompt | `~/.workbuddy/skills/...` | 技能路径引用 |

导入时必须检查这些路径在目标设备上是否存在，并提示用户修正。

### 不直接操作数据库

此技能通过 `automation_update` 工具的官方 API 进行操作，
不直接读写 SQLite 数据库文件，避免数据库损坏风险。

### 加密建议

对于包含敏感信息的导出文件，建议用户：
1. 使用密码压缩（如 7z、zip 加密）
2. 存储在加密分区或加密网盘
3. 不要通过即时通讯工具明文传输

## Limitations

- 导入时无法保留原始任务的 `id`，系统会生成新 ID
- `automation_runs`（执行历史）不会迁移，仅迁移任务配置
- 导入后任务的下次执行时间取决于 rrule 规则和当前时间
- 如果原始任务依赖特定的 MCP 连接器（connectorIds），目标设备需要手动启用对应连接器
