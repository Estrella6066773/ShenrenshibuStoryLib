# 在仓库任意子目录运行：将 Git hooks 指向「正文/管线/检查/」目录
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    $root = (git -C "../../.." rev-parse --show-toplevel 2>$null)
    if (-not $root) {
        $root = git rev-parse --show-toplevel 2>$null
    }
    if (-not $root) { throw "请在 ShenrenshibuStoryLib 仓库内运行此脚本" }
    Set-Location $root
    git config core.hooksPath "正文/管线/检查"
    Write-Host "已设置 core.hooksPath = 正文/管线/检查"
    Write-Host "提交时将自动运行 check-links.py"
} finally {
    Pop-Location
}
