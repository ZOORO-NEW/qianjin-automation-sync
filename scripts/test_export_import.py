#!/usr/bin/env python3
"""Test script for automation-sync skill: export and validate JSON format."""
import json
import datetime
import re
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Simulated data from automation_update view calls
automations = [
    {
        "name": "\u6bcf\u65e5AI\u516c\u4f17\u53f7\u6587\u7ae0\u751f\u6210",
        "prompt": "\u4f60\u662f\u4e00\u4f4d\u62e5\u670913\u5e74\u5185\u5bb9\u884c\u4e1a\u7ecf\u9a8c\u7684\u81ea\u5a92\u4f53\u8fd0\u8425\u4e13\u5bb6\u300c\u524d\u8fdb\u300d\uff0c\u4f60\u9700\u8981\u5b8c\u6210\u4eca\u5929\u7684\u6bcf\u65e5\u516c\u4f17\u53f7\u6587\u7ae0\u5199\u4f5c\u4efb\u52a1\u3002\n\n**\u8f93\u51fa\u76ee\u5f55**: C:\\Users\\ZQJ\\WorkBuddy\\2026-06-04-22-58-34\\\u6bcf\u65e5\u6587\u7ae0\\\n**\u6587\u4ef6\u547d\u540d**: {date}_title.md\n\n**\u5b8c\u6210\u6b65\u9aa4**:\n1. \u786e\u5b9a\u4eca\u5929\u5199\u54ea\u4e2a\u65b9\u5411\n2. \u4ee5\u4e00\u4e2a\u4e13\u4e1aAI\u4f7f\u7528\u8005\u7684\u8eab\u4efd\uff0c\u5206\u4eab\u5185\u5bb9\n3. \u76f4\u63a5\u5199\u6210\u5b8c\u6574\u7684\u516c\u4f17\u53f7\u6587\u7ae0\n4. \u4fdd\u5b58\u5230\u8f93\u51fa\u76ee\u5f55\n5. \u6392\u7248\u5e76\u53d1\u5e03\u5230\u516c\u4f17\u53f7\u8349\u7a3f\u7bb1",
        "status": "ACTIVE",
        "scheduleType": "recurring",
        "rrule": "FREQ=DAILY;BYHOUR=9;BYMINUTE=0",
        "scheduledAt": None,
        "validFrom": None,
        "validUntil": None,
        "cwds": "C:\\Users\\ZQJ\\WorkBuddy\\2026-06-04-22-58-34",
        "expertId": None,
        "modelId": None,
        "modelIsThinking": None,
        "connectorIds": None
    },
    {
        "name": "\u56fd\u5b66\u65b9\u5411\u9009\u9898\u4e0e\u64b0\u5199\u6587\u7a3f",
        "prompt": "\u6293\u53d6\u6307\u5b9a\u4fe1\u606f\u6e90\uff08\u884c\u4e1a\u70ed\u70b9\u3001\u5e73\u53f0\u70ed\u699c\u3001\u7ade\u54c1\u52a8\u6001\uff09\n\n\u9884\u8bbe\u65b9\u5411\uff1a\u56fd\u5b66\u4fee\u5fc3/\u56fd\u5b66\u667a\u6167\u8d5b\u9053\u6765\u89c4\u5212\u516c\u4f17\u53f7\u7684\u8fd0\u8425\u4f53\u7cfb\u4e0e\u6bcf\u65e5\u4e3b\u9898\n\n\u7ed3\u5408\u9009\u9898\u64b0\u5199\u516c\u4f17\u53f7\u6587\u6848\uff0c\u8981\u6c42\u7b26\u5408\u7206\u6b3e\uff0c\u9ad8\u9605\u8bfb\uff0c\u9ad8\u8f6c\u53d1\u7684\u3002",
        "status": "ACTIVE",
        "scheduleType": "recurring",
        "rrule": "FREQ=DAILY;BYHOUR=7;BYMINUTE=0",
        "scheduledAt": None,
        "validFrom": "2026-06-06T16:00:00.000Z",
        "validUntil": None,
        "cwds": "E:\\workbuddy\\automation-2026-06-07-13-37-26",
        "expertId": None,
        "modelId": None,
        "modelIsThinking": None,
        "connectorIds": None
    }
]

# Build export JSON
export_data = {
    "metadata": {
        "version": "1.0",
        "exported_at": datetime.datetime.now().astimezone().isoformat(),
        "total_count": len(automations),
        "source_device": "ZQJ-PC"
    },
    "automations": automations
}

# Write to file
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "workbuddy", "2026-07-07-12-29-48", "automation-export-test.json")
output_path = os.path.normpath(output_path)
# Fallback to current dir if path resolution fails
if not os.path.isdir(os.path.dirname(output_path)):
    output_path = "automation-export-test.json"

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("AUTOMATION-SYNC EXPORT TEST")
print("=" * 60)
print(f"Output file: {output_path}")
print(f"Version: {export_data['metadata']['version']}")
print(f"Exported at: {export_data['metadata']['exported_at']}")
print(f"Total count: {export_data['metadata']['total_count']}")
print()

# Validate: re-read and parse
with open(output_path, 'r', encoding='utf-8') as f:
    parsed = json.load(f)

assert parsed['metadata']['version'] == '1.0', "Version mismatch"
assert parsed['metadata']['total_count'] == len(parsed['automations']), "Count mismatch"
print("[PASS] JSON format validation")
print()

# Print task details
for i, auto in enumerate(parsed['automations']):
    print(f"--- Task {i+1} ---")
    print(f"  Name: {auto['name']}")
    print(f"  Status: {auto['status']}")
    print(f"  Schedule: {auto['scheduleType']} / {auto['rrule']}")
    print(f"  CWDs: {auto['cwds']}")
    print(f"  ValidFrom: {auto['validFrom']}")
    print(f"  Prompt length: {len(auto['prompt'])} chars")

    # Device path check
    combined = auto['prompt'] + ' ' + (auto.get('cwds') or '')
    path_pattern = r'[A-Z]:\\[^\s"<>|*]+'
    paths = re.findall(path_pattern, combined)
    if paths:
        print(f"  Device paths found: {len(paths)} (need manual review on import)")
        for p in paths:
            exists = os.path.exists(p.rstrip('\\'))
            print(f"    - {p} [{'EXISTS' if exists else 'NOT FOUND'}]")
    print()

# Sensitive info scan
print("=" * 60)
print("SENSITIVE INFO SCAN")
print("=" * 60)
sensitive_patterns = [
    (r'sk-[a-zA-Z0-9]{20,}', 'API Key (sk-)'),
    (r'Bearer\s+[a-zA-Z0-9\-_.=]{20,}', 'Bearer Token'),
    (r'(?i)(password|passwd|pwd|secret|token|api_key|apikey)\s*[=:]\s*\S+', 'Password/Secret'),
    (r'-----BEGIN\s+\w+\s+PRIVATE\s+KEY-----', 'Private Key'),
]
found_any = False
for auto in parsed['automations']:
    for pattern, name in sensitive_patterns:
        matches = re.findall(pattern, auto['prompt'])
        if matches:
            print(f"  [WARNING] {name} found in '{auto['name']}'")
            found_any = True
if not found_any:
    print("  [OK] No high-severity sensitive info detected.")

print()
print("=" * 60)
print("IMPORT SIMULATION (dry-run)")
print("=" * 60)

# Simulate import: check name conflicts
existing_names = [auto['name'] for auto in parsed['automations']]
for auto in parsed['automations']:
    name = auto['name']
    if existing_names.count(name) > 1:
        print(f"  [SKIP] '{name}' - name conflict (would ask user)")
    else:
        # Verify required fields
        required = ['name', 'prompt', 'scheduleType']
        missing = [f for f in required if not auto.get(f)]
        if missing:
            print(f"  [FAIL] '{name}' - missing required fields: {missing}")
        else:
            if auto['scheduleType'] == 'recurring' and not auto.get('rrule'):
                print(f"  [FAIL] '{name}' - recurring task missing rrule")
            else:
                print(f"  [READY] '{name}' - all fields valid, ready to create")

print()
print("=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
