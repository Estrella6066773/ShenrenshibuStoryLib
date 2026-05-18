#!/usr/bin/env python3
"""校验「正文/」下 Markdown 内部相对链接、注册表路径与玩家 manifest。

用法（在仓库根目录）：
    python 正文/管线/检查/check-links.py
    python 正文/管线/检查/check-links.py --fix-malformed   # 仅修复缺 ]( 的畸形链接

退出码：0 = 全部通过；1 = 存在断链、畸形链接或登记不一致。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
# 缺 ]( 的常见笔误：[WLD-03../../../00-基石/foo.md)
MALFORMED_RE = re.compile(r"\[([A-Z][A-Z0-9-]*)(\.\./)+([^)\]]+\.md)\)")
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
REGISTRY_PATH_RE = re.compile(r"^\s+path:\s+(.+?)\s*$")
REGISTRY_ID_RE = re.compile(r"^\s+-\s+id:\s+(\S+)\s*$")
MANIFEST_ID_RE = re.compile(r"^\s+-\s+([A-Z][A-Z0-9-]+)\s*$")
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def strip_non_prose(text: str) -> str:
    """去掉代码块与行内代码，避免把规则文档中的反例当成真链接。"""
    text = FENCED_CODE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def canon_root() -> Path:
    return Path(__file__).resolve().parents[2]  # 正文/


def repo_root() -> Path:
    return canon_root().parent


def load_registry(root: Path) -> list[tuple[str, str]]:
    reg_path = root / "治理/id-registry.yaml"
    entries: list[tuple[str, str]] = []
    current_id: str | None = None
    for line in reg_path.read_text(encoding="utf-8").splitlines():
        m_id = REGISTRY_ID_RE.match(line)
        if m_id:
            current_id = m_id.group(1)
            continue
        m_path = REGISTRY_PATH_RE.match(line)
        if m_path and current_id:
            entries.append((current_id, m_path.group(1)))
            current_id = None
    return entries


def load_manifest_ids(root: Path) -> list[str]:
    manifest = root / "玩家投放/v0.1/manifest.yaml"
    ids: list[str] = []
    in_canon = False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip() == "canon_ids:":
            in_canon = True
            continue
        if not in_canon:
            continue
        if line and not line[0].isspace():
            break
        m = MANIFEST_ID_RE.match(line)
        if m:
            ids.append(m.group(1))
    return ids


def scan_links(root: Path) -> tuple[list[tuple[str, str, str]], list[tuple[str, str]], int]:
    broken: list[tuple[str, str, str]] = []
    malformed: list[tuple[str, str]] = []
    ok = 0

    for md in sorted(root.rglob("*.md")):
        text = strip_non_prose(md.read_text(encoding="utf-8"))
        rel = str(md.relative_to(root))

        for m in MALFORMED_RE.finditer(text):
            malformed.append((rel, m.group(0)))

        for m in LINK_RE.finditer(text):
            target = m.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                broken.append((rel, target, m.group(0)))
            else:
                ok += 1

    return broken, malformed, ok


def scan_registry(root: Path) -> list[str]:
    issues: list[str] = []
    registry_ids: set[str] = set()
    for entry_id, rel_path in load_registry(root):
        registry_ids.add(entry_id)
        target = root / rel_path
        if not target.is_file():
            issues.append(f"注册表 {entry_id} 路径不存在：{rel_path}")
    return issues, registry_ids


def scan_manifest(root: Path, registry_ids: set[str]) -> list[str]:
    issues: list[str] = []
    for mid in load_manifest_ids(root):
        if mid not in registry_ids:
            issues.append(f"manifest canon_ids 未登记：{mid}")
    return issues


def fix_malformed(root: Path) -> int:
    count = 0
    for md in root.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        new, n = MALFORMED_RE.subn(
            lambda m: f"[{m.group(1)}]({m.group(2)}{m.group(3)})", text
        )
        if n:
            md.write_text(new, encoding="utf-8")
            count += n
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="校验正文 Markdown 内部链接与登记一致性")
    parser.add_argument(
        "--fix-malformed",
        action="store_true",
        help="自动修复缺 ]( 的畸形链接（修复后须人工核对相对路径层级）",
    )
    args = parser.parse_args()

    root = canon_root()
    if not root.is_dir():
        print(f"找不到正文目录：{root}", file=sys.stderr)
        return 1

    if args.fix_malformed:
        n = fix_malformed(root)
        print(f"已尝试修复畸形链接 {n} 处；请重新运行校验并人工核对路径。")

    broken, malformed, ok = scan_links(root)
    reg_issues, registry_ids = scan_registry(root)
    manifest_issues = scan_manifest(root, registry_ids)

    if malformed:
        print(f"畸形链接（缺 ]( ）：{len(malformed)}")
        for rel, snippet in malformed:
            print(f"  {rel}\n    {snippet}")

    if broken:
        print(f"断链：{len(broken)}")
        for rel, target, snippet in broken:
            print(f"  {rel}\n    目标: {target}\n    {snippet}")

    if reg_issues:
        print(f"注册表路径问题：{len(reg_issues)}")
        for msg in reg_issues:
            print(f"  {msg}")

    if manifest_issues:
        print(f"manifest 登记问题：{len(manifest_issues)}")
        for msg in manifest_issues:
            print(f"  {msg}")

    total_bad = len(broken) + len(malformed) + len(reg_issues) + len(manifest_issues)
    if total_bad:
        print("\n书写约定见：正文/治理/03-内部链接书写规则.md")
        return 1

    md_count = len(list(root.rglob("*.md")))
    print(
        f"校验通过：{md_count} 个 Markdown 文件，{ok} 条相对链接可解析；"
        f"注册表 {len(registry_ids)} 条，manifest {len(load_manifest_ids(root))} 条 id 均已登记。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
