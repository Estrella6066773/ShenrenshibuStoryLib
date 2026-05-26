# 输出文档元数据用的「最后更新」日期（本机本地时间，非网络）
# 用法:
#   .\Scripts\Get-DocsDate.ps1           # 2026-05-21
#   .\Scripts\Get-DocsDate.ps1 -Full     # 2026-05-21 17:34:12 +08:00
#   .\Scripts\Get-DocsDate.ps1 -Utc      # UTC 日期（仅当明确要求 UTC 时用）

param(
    [switch]$Full,
    [switch]$Utc
)

$now = if ($Utc) { [DateTime]::UtcNow } else { Get-Date }

if ($Full) {
    if ($Utc) {
        $now.ToString("yyyy-MM-dd HH:mm:ss 'UTC'")
    } else {
        $now.ToString("yyyy-MM-dd HH:mm:ss K")
    }
} else {
    $now.ToString("yyyy-MM-dd")
}
