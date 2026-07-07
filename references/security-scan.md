# Sensitive Information Scan Rules

Detailed rules for scanning sensitive information in automation task prompts before export.

## Scan Patterns

### API Keys

```
Pattern: (sk-[a-zA-Z0-9]{20,})|(ak_[a-zA-Z0-9]{16,})|(AKID[a-zA-Z0-9]{32,})
Severity: HIGH
Action: Warn user, offer redaction
```

Common API key formats:
- OpenAI: `sk-` followed by 48+ alphanumeric characters
- AWS: `AKIA` followed by 16 characters
- Tencent Cloud: `AKID` followed by 32+ characters
- Aliyun: `LTAI` followed by 12+ characters
- Custom: `ak_` prefix

### Bearer Tokens

```
Pattern: (Bearer\s+[a-zA-Z0-9\-_\.=]{20,})
Severity: HIGH
Action: Warn user, offer redaction
```

### Password Assignments

```
Pattern: (?i)(password|passwd|pwd|secret|token|api_key|apikey)\s*[=:]\s*\S+
Severity: HIGH
Action: Warn user, offer redaction
```

### Private Keys

```
Pattern: -----BEGIN\s+(RSA\s+|EC\s+|OPENSSH\s+|PGP\s+)?PRIVATE\s+KEY-----
Severity: CRITICAL
Action: Warn user, offer redaction
```

### Connection String Credentials

```
Pattern: [a-zA-Z]+://[^:\s]+:[^@\s]+@[a-zA-Z0-9\-\.]+
Severity: HIGH
Action: Warn user, offer redaction
```

### File System Paths (Device-Specific)

```
Pattern: ([A-Z]:\\[^\s"'<>|*?]+)|(\/home\/[^\s"'<>|*?]+)|(\/Users\/[^\s"'<>|*?]+)
Severity: LOW
Action: Flag for user review (not redacted, but user should verify path exists on target device)
```

Windows paths: `C:\Users\username\...`
Unix paths: `/home/username/...` or `/Users/username/...`
These paths may not exist on the target device.

## Redaction Strategy

When user chooses to redact sensitive information:

1. Replace the matched sensitive value with `***REDACTED***`
2. Preserve surrounding context (variable names, prefixes) for readability
3. Log a summary of redacted items (count by type) in the export report

Example:
```
Before: export API_KEY="sk-abc123def456..."
After:  export API_KEY="***REDACTED***"
```

## Device Path Compatibility

Paths found in `cwds` and `prompt` fields need manual review when migrating across devices.

### Common Path Patterns to Check

| Source Pattern | Example | Migration Action |
|----------------|---------|------------------|
| Windows user home | `C:\Users\ZQJ\...` | Replace username, verify path exists |
| WorkBuddy workspace | `C:\Users\ZQJ\WorkBuddy\2026-xx-xx-...` | These are session-specific, likely need new path |
| WorkBuddy skills | `~/.workbuddy/skills/...` | Usually portable across devices |
| Temp directories | `C:\Users\ZQJ\AppData\Local\Temp\...` | Not portable, remove or replace |
| Network shares | `\\server\share\...` | Verify accessible from target device |

### Import-Time Path Validation

During import, for each task:
1. Extract all paths from `cwds` field (split by comma)
2. Extract paths from `prompt` using the file system path pattern
3. Check if each path exists on the current device
4. If path does not exist, add to warning list
5. Present warning list to user before creating the task
