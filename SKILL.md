---
version: 1.0.0
slug: qianjin-automation-sync
displayName: 自动化任务跨设备备份同步
summary: "'WorkBuddy 自动化任务与已安装技能的全量跨设备备份、导出、导入与迁移工具。当用户需要备份自动化任务、导出/导入技能、迁移自动化到新设备、跨电脑同步全部配置时使用此技能。触发词包括：导出自动化、备份自动化、导入自动化、迁移自动..."
license: MIT
name: qianjin-automation-sync
category: 效率工具
platforms: [workbuddy, claude-code, cursor, windsurf, codex]
description: "WorkBuddy 自动化任务与已安装技能的全量跨设备备份、导出、导入与迁移工具。当用户需要备份自动化任务、导出/导入技能、迁移自动化到新设备、跨电脑同步全部配置时使用此技能。触发词包括：导出自动化、备份自动化、导入自动化、迁移自动化、同步自动化任务、automation export/import/backup/restore/sync/migrate、换电脑自动化任务没了、自动化任务跨设备、automation backup。此技能通过 automation_update 工具的 list/view/create 模式 + skills 目录打包实现，不直接操作 SQLite 数据库，确保操作安全可靠。"
agent_created: true
disable: false
---

# Qianjin Automation Sync

> **全量跨设备同步工具**：一键导出/导入自动化任务 + 已安装的所有技能文件。解决换电脑后重配自动化、重装技能的痛点。

---

## Overview

WorkBuddy 的自动化任务（SQLite 数据库）和已安装技能（`~/.workbuddy/skills/` 目录）默认只存储在本地，不支持跨设备云同步。

此技能提供**全量打包式导出/导入**流程：

```
┌─ 导出 ─────────────────────────────────┐
│  automation.json  ← 自动化任务配置      │
│  skills/          ← 所有已安装的技能文件 │
│  └── qianjin-writer/SKILL.md         │
│  └── qianjin-oral-video/...           │
│  └── ...                              │
│  └── package.zip (加密可选)            │
└────────────────────────────────────────┘
```

旧电脑 → 导出 ZIP → 网盘/U盘 → 新电脑 → 导入 → 自动化+技能全部还原

---

## When to Use

- 用户需要备份当前所有自动化任务 + 已安装的技能
- 用户换了新电脑，想把旧电脑的自动化 + 技能全部迁移过来
- 用户重装了系统，需要恢复 WorkBuddy 完整配置
- 用户有多个设备（办公/家用），想保持自动化任务和技能一致
- 用户想把自己的技能配置分享给另一台电脑的另一个账号

---

## 使用说明（用户指南）

### 场景一：我要换新电脑了

**旧电脑上操作：**
> "导出我的全部配置" 或 "帮我打包迁移"

技能会自动完成：
1. 备份所有自动化任务 → `automation.json`
2. 备份所有已安装的技能 → `skills/` 目录
3. 打包为 ZIP → `workbuddy-backup-2026-07-14.zip`
4. 提醒你：**用 U 盘/网盘把 ZIP 文件复制到新电脑**

**新电脑上操作（同账号或不同账号均可）：**
> "帮我导入配置" 然后把 ZIP 文件路径给它

技能会自动完成：
1. 解包 ZIP
2. 导入所有自动化任务（自动跳过重名任务）
3. 把所有技能复制到新电脑
4. 提示你：重新打开 WorkBuddy 即可生效

### 场景二：我只想同步自动化任务（不要技能）

> "导出自动化任务" 或 "备份自动化"

只导出 `automation.json`，不打包技能文件夹。

### 场景三：我只想同步技能文件（不要自动化任务）

> "导出已安装的技能" 或 "备份技能"

只打包 `skills/` 目录，不导出自动化任务。

---

## Export Workflow（全量导出）

### Step 1: 询问用户导出范围

首先确认用户想导出什么：

| 选项 | 说明 |
|------|------|
| **全量导出**（推荐） | 自动化任务 + 所有技能文件 → ZIP |
| 仅自动化任务 | 只导出 automation.json |
| 仅技能文件 | 只打包 skills/ 目录 |

默认为**全量导出**，除非用户明确指定范围。

### Step 2: 导出自动化任务

同前版流程：
1. 调用 `automation_update`，`mode="list"` 获取所有任务摘要
2. 逐条调用 `automation_update`，`mode="view"` 获取完整配置
3. 提取所有字段（name, prompt, status, scheduleType, rrule 等）
4. 执行敏感信息扫描（API Key、Token、密码、私钥等模式）
5. 将任务配置组装为 JSON

### Step 3: 导出技能文件

扫描 `~/.workbuddy/skills/` 目录下的所有技能文件夹：

```python
skills_dir = os.path.expanduser("~/.workbuddy/skills")
# 每个子目录都是一个技能的文件夹
# 例如：qianjin-writer、qianjin-oral-video、qianjin-ip-design ...
```

对每个技能文件夹执行：

| 检查项 | 说明 |
|--------|------|
| ✅ 必须有 `SKILL.md` 才视为有效技能 | 空目录/无 SKILL.md 的文件夹跳过 |
| ✅ 全量复制该文件夹下所有文件 | SKILL.md、scripts/、references/、README.md、assets/ 等 |
| ⚠️ 跳过 `.git/` 目录 | 避免打包完整的 git 历史（太大） |
| ⚠️ 跳过 `__pycache__/` 目录 | Python 缓存文件不需要迁移 |
| ⚠️ 跳过 `node_modules/` 目录 | 太大，目标设备需重新 npm install |
| ⚠️ 文件过大警告 | 单个文件超过 10MB 时提醒用户 |

列出所有将要导出的技能清单给用户确认，包括每个技能的版本号（从 frontmatter 提取）。

### Step 4: 打包为 ZIP

```javascript
workbuddy-backup-{YYYY-MM-DD}.zip
├── metadata.json          # 元信息（导出时间、设备名、内容清单）
├── automation.json        # 自动化任务配置
└── skills/                # 技能文件目录
    ├── qianjin-writer/
    │   ├── SKILL.md
    │   ├── README.md
    │   └── prompts/...
    ├── qianjin-oral-video/
    │   ├── SKILL.md
    │   └── scripts/...
    └── ...
```

`metadata.json` 格式：
```json
{
  "exported_at": "2026-07-14T16:00:00+08:00",
  "source_device": "DESKTOP-XXXX",
  "source_user": "ZQJ",
  "content": {
    "has_automations": true,
    "automation_count": 5,
    "has_skills": true,
    "skill_count": 4,
    "skills_list": [
      {"name": "qianjin-writer", "version": "2.0"},
      {"name": "qianjin-oral-video", "version": "1.0"},
      {"name": "qianjin-commerce-toolkit", "version": "2.0"},
      {"name": "qianjin-ip-design", "version": "1.0"}
    ]
  }
}
```

### Step 5: 敏感信息处理

- 对 `automation.json` 中每条任务的 `prompt` 字段执行敏感信息扫描
- 对技能文件中的以下**潜在敏感路径**进行扫描：
  - `prompts/` 目录下的 API Key、Token、密码等
  - `scripts/` 中的硬编码凭据
  - `references/` 中的凭证信息
- 扫描出敏感信息后，向用户提供选项：脱敏替换 or 原样导出

### Step 6: 路径映射建议

自动生成 `path-mapping.json`，记录所有源设备路径：
```json
{
  "source_cwds": ["C:\\Users\\ZQJ\\WorkBuddy\\项目A"],
  "skills_containing_abs_paths": ["qianjin-writer"],
  "path_hints": [
    "qianjin-writer/scripts/generate_video.py 中引用: C:\\Users\\ZQJ\\...\\ffmpeg.exe",
    "qianjin-commerce-toolkit/SKILL.md 中引用: C:\\Users\\ZQJ\\..."
  ]
}
```

导入时可根据此映射提示用户替换为新设备的对应路径。

### Step 7: 输出摘要

导出完成后，向用户展示：

```
✅ 导出完成！

📦 ZIP 文件：E:/workbuddy/.../workbuddy-backup-2026-07-14.zip
├── 自动化任务：5 条（已脱敏处理）
├── 技能文件：4 个（总大小 2.3MB）
└── 路径映射建议：已生成

📋 技能清单：
  1. qianjin-writer v2.0
  2. qianjin-oral-video v1.0
  3. qianjin-commerce-toolkit v2.0
  4. qianjin-ip-design v1.0

📌 下一步：
  把 ZIP 文件复制到目标设备，然后运行导入流程：
  "导入配置 from E:/路径/.../workbuddy-backup-2026-07-14.zip"
```

---

## Import Workflow（全量导入）

### Step 1: 读取并解包 ZIP 文件

```python
import zipfile
with zipfile.ZipFile(zip_path, 'r') as zf:
    zf.extractall(temp_extract_dir)
```

- 验证 `metadata.json` 文件存在且格式正确
- 检查 `metadata.version` 版本兼容性
- 读取内容清单，了解包中包含哪些数据

### Step 2: 导入自动化任务（如有）

同前版流程：
1. 读取 `automation.json`（如果存在）
2. 获取当前设备已有任务列表（按 name 去重）
3. 逐条创建，重名时询问：跳过 / 创建副本（`_imported_时间戳`）

### Step 3: 导入技能文件（如有）

将 `skills/` 目录下所有技能文件夹复制到目标设备的 `~/.workbuddy/skills/`：

```python
target_skills_dir = os.path.expanduser("~/.workbuddy/skills")
os.makedirs(target_skills_dir, exist_ok=True)

for skill_name in os.listdir(temp_skills_dir):
    skill_path = os.path.join(temp_skills_dir, skill_name)
    target_path = os.path.join(target_skills_dir, skill_name)
    
    if os.path.exists(target_path):
        # 询问用户：覆盖 / 跳过 / 保留两者
        ...
    else:
        shutil.copytree(skill_path, target_path)
```

对每个技能的处理规则：

| 情况 | 默认行为 |
|------|---------|
| 目标设备不存在此技能 | ✅ 直接复制 |
| 目标设备已有同名技能 | 🔶 询问：覆盖 / 跳过 / 保留两者（重命名） |
| 技能中引用了源设备路径 | ⚠️ 列出所有需要手动更新的路径 |

### Step 4: 路径重映射

读取 `path-mapping.json`（如果有），向用户展示所有需要手动更新的路径：

```
⚠️ 以下路径在目标设备上可能不适用，请确认：

qianjin-writer/scripts/generate_video.py 第29行：
  C:\Users\ZQJ\AppData\...\ffmpeg.exe
  → 你的新电脑上 FFmpeg 安装在？[用户回答]

qianjin-commerce-toolkit/SKILL.md 第15行：
  C:\Users\ZQJ\...\工作目录
  → 请替换为你的实际路径
```

对于 `automation` 中的 `cwds` 字段，提示用户手动设置。

### Step 5: 输出导入报告

```
✅ 导入完成！

📋 自动化任务：5 条
  ├── 成功导入：4 条
  ├── 跳过（重名）：1 条 ─ "每日热点监控"
  └── 失败：0 条

📦 技能文件：4 个
  ├── 新安装：3 个
  ├── 已存在已覆盖：1 个 ─ qianjin-writer
  └── 路径需手动修正：2 条（详见上方）

🔔 请重启 WorkBuddy 使新技能生效。
```

---

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

---

## Security & Compatibility Notes

### 敏感信息

自动化任务的 `prompt` 字段和技能文件的脚本/配置可能包含 API Key、密码、文件路径等敏感信息。导出前务必执行敏感信息扫描。ZIP 文件应存储在安全位置，避免公开共享。

### 跨账号兼容性

| 场景 | 能否导入 | 说明 |
|------|---------|------|
| 同账号→同设备（重装） | ✅ | 完全兼容，无任何冲突 |
| 同账号→不同设备 | ✅ | 仅需修正设备特定路径 |
| 不同账号→不同设备 | ✅ | 同上。技能文件是纯文件，不绑定 WorkBuddy 账号 |
| 不同操作系统（Win→Mac） | ⚠️ | 路径格式不同（`C:\...` vs `/Users/...`），需手动修正所有路径 |

### 设备路径兼容性

以下字段可能包含设备特定路径，跨设备迁移时需要手动修正：

| 字段 | 路径示例 | 说明 |
|------|----------|------|
| cwds | `C:\Users\ZQJ\WorkBuddy\...` | 工作目录路径 |
| prompt | `C:\Users\ZQJ\...\输出目录\` | prompt 中引用的文件路径 |
| prompt | `~/.workbuddy/skills/...` | 技能路径引用 |
| 脚本中硬编码 | `/c/Users/ZQJ/...\ffmpeg.exe` | 技能脚本内的绝对路径 |

导入时必须检查这些路径在目标设备上是否存在，并提示用户修正。

### 不直接操作数据库

此技能通过 `automation_update` 工具的官方 API 进行操作，不直接读写 SQLite 数据库文件，避免数据库损坏风险。

### 加密建议

对于包含敏感信息的导出文件，建议用户：
1. 使用密码压缩（如 7z、zip 加密）
2. 存储在加密分区或加密网盘
3. 不要通过即时通讯工具明文传输

---

## Limitations

- 导入时无法保留原始任务的 `id`，系统会生成新 ID
- `automation_runs`（执行历史）不会迁移，仅迁移任务配置
- 导入后任务的下次执行时间取决于 rrule 规则和当前时间
- 如果原始任务依赖特定的 MCP 连接器（connectorIds），目标设备需要手动启用对应连接器
- 技能中的大文件（>10MB 如模型文件、数据集）不会自动打包，需单独迁移
- 跨操作系统迁移（Win↔Mac）时，技能中的硬编码路径需手动修正
- WorkBuddy 需要重启后新导入的技能才能生效
