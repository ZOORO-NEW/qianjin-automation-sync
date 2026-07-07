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

安装后重启 WorkBuddy，对它说"导出自动化"或"备份自动化"即可触发。

## 如何使用

### 快速开始（3步）

**第一步：导出（在旧电脑上）**

打开 WorkBuddy，直接说：
> 导出自动化任务

WorkBuddy 会自动完成以下操作：
1. 列出你所有的自动化任务
2. 逐条读取完整配置（名称、指令、调度规则、工作目录等）
3. 扫描敏感信息（API Key、密码、私钥），发现后询问你是否脱敏
4. 生成一个 JSON 文件，默认保存到当前工作目录

你也可以指定输出路径：
> 导出自动化任务到 D:\backup\

**第二步：传输文件**

将导出的 JSON 文件通过以下任意方式传到新电脑：
- 网盘（百度网盘、微云、OneDrive 等）
- U 盘 / 移动硬盘
- Git 仓库
- 即时通讯工具发送给自己（注意：如果包含敏感信息，建议先加密压缩）

**第三步：导入（在新电脑上）**

打开 WorkBuddy，说：
> 导入自动化任务，文件路径是 D:\backup\automation-export-2026-07-07.json

WorkBuddy 会自动完成以下操作：
1. 读取 JSON 文件并验证格式
2. 检查与现有任务是否重名，重名时询问你跳过还是创建副本
3. 逐条创建自动化任务
4. 检查工作目录路径是否存在于新电脑上，不存在的给出警告
5. 输出导入报告（成功数 / 跳过数 / 失败数）

### 常见使用场景

| 场景 | 操作 |
|------|------|
| 换新电脑前备份 | 旧电脑执行"导出自动化任务" → 网盘传文件 |
| 新电脑恢复自动化 | 新电脑执行"导入自动化任务，文件路径是 xxx.json" |
| 定期备份 | 每月执行一次"导出自动化任务"，保存到固定目录 |
| 审计任务配置 | 执行"导出自动化任务"，查看 JSON 了解所有任务的完整配置 |
| 团队共享自动化 | A 导出 → B 导入（注意检查设备路径和敏感信息） |

### 触发词

以下说法都能触发此技能：

| 触发词 | 意图 |
|--------|------|
| 导出自动化 / 导出自动化任务 | 导出 |
| 备份自动化 / 备份自动化任务 | 导出 |
| 导入自动化 / 导入自动化任务 | 导入 |
| 迁移自动化 / 迁移自动化任务 | 导入 |
| 同步自动化 / 同步自动化任务 | 导入 |
| 换电脑自动化任务没了 | 导入 |
| automation export / backup / import | 导出/导入 |

### 导出示例

```
用户：导出自动化任务

WorkBuddy：正在导出你的自动化任务...
  ✅ 已获取 5 条自动化任务
  ✅ 敏感信息扫描完成（未发现高风险内容）
  ✅ 已生成导出文件

导出报告：
  文件路径：E:\workbuddy\automation-export-2026-07-07.json
  任务总数：5
  - 每日AI公众号文章生成 [ACTIVE] [每日 09:00]
  - 国学方向选题与撰写文稿 [ACTIVE] [每日 07:00]
  - 每周热点选题推送 [ACTIVE] [每周一 09:00]
  - 月度数据报告生成 [ACTIVE] [每月1日 10:00]
  - 每日AI资讯日报 [PAUSED] [每日 08:00]

⚠️ 设备路径提醒：以下路径在导入到其他设备时需要手动修正：
  - C:\Users\ZQJ\WorkBuddy\2026-06-04-22-58-34
  - E:\workbuddy\automation-2026-06-07-13-37-26
```

### 导入示例

```
用户：导入自动化任务，文件路径是 D:\backup\automation-export-2026-07-07.json

WorkBuddy：正在导入自动化任务...
  ✅ JSON 格式验证通过
  ✅ 检测到 5 条任务，其中 0 条与现有任务重名

导入报告：
  ✅ 成功导入：5 条
  ⏭️ 跳过：0 条
  ❌ 失败：0 条

⚠️ 路径检查警告：以下任务的工作目录在当前设备上不存在，请手动修正：
  - "每日AI公众号文章生成" → C:\Users\ZQJ\WorkBuddy\2026-06-04-22-58-34
    建议：请将 cwds 更新为当前设备上的对应路径
  - "国学方向选题与撰写文稿" → E:\workbuddy\automation-2026-06-07-13-37-26
    建议：请将 cwds 更新为当前设备上的对应路径
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

## Security

- 导出前自动扫描敏感信息（API Key、Bearer Token、密码、私钥、连接字符串凭证）
- 发现敏感信息时提供两个选项：脱敏导出或原样导出（需用户确认风险）
- 建议将包含敏感信息的导出文件加密压缩后存储
- 不通过即时通讯工具明文传输导出文件

## Limitations

- 导入时无法保留原始任务的 `id`，系统会生成新 ID
- `automation_runs`（执行历史）不会迁移，仅迁移任务配置
- 导入后任务的下次执行时间取决于 rrule 规则和当前时间
- 如果原始任务依赖特定的 MCP 连接器（connectorIds），目标设备需要手动启用对应连接器

## Requirements

- WorkBuddy 桌面版
- `automation_update` 工具（WorkBuddy 内置）

## License

MIT
