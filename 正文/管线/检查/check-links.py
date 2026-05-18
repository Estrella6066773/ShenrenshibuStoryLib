#!/usr/bin/env python3
"""校验「正文/」下 Markdown 内部相对链接、注册表路径与玩家 manifest。

用法（在仓库根目录）：
    python 正文/管线/检查/check-links.py
    python 正文/管线/检查/check-links.py --fix              # 尝试自动修正链接后复检
    python 正文/管线/检查/check-links.py --fix --stage-fixed  # 修正并把变更 git add（供 pre-commit）

退出码：0 = 全部通过；1 = 存在无法自动修复的问题。
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
MALFORMED_RE = re.compile(r"\[([A-Z][A-Z0-9-]*)(\.\./)+([^)\]]+\.md)\)")
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
REGISTRY_PATH_RE = re.compile(r"^\s+path:\s+(.+?)\s*$")
REGISTRY_ID_RE = re.compile(r"^\s+-\s+id:\s+(\S+)\s*$")
MANIFEST_ID_RE = re.compile(r"^\s+-\s+([A-Z][A-Z0-9-]+)\s*$")
LINKABLE_EXT = {".md", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def strip_non_prose(text: str) -> str:
    text = FENCED_CODE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def forbidden_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for pat in (FENCED_CODE_RE, INLINE_CODE_RE):
        for m in pat.finditer(text):
            ranges.append((m.start(), m.end()))
    return ranges


def pos_forbidden(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s <= pos < e for s, e in ranges)


def canon_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


class LinkIndex:
    def __init__(self, root: Path, registry: list[tuple[str, str]]):
        self.root = root
        self.id_to_path: dict[str, Path] = {
            entry_id: Path(rel) for entry_id, rel in registry
        }
        self.ids_by_length = sorted(self.id_to_path.keys(), key=len, reverse=True)
        self.by_name: dict[str, list[str]] = defaultdict(list)
        for f in root.rglob("*"):
            if f.is_file() and f.suffix.lower() in LINKABLE_EXT:
                self.by_name[f.name].append(f.relative_to(root).as_posix())

    def id_from_filename(self, name: str) -> str | None:
        for entry_id in self.ids_by_length:
            if name.startswith(entry_id + "-") or name == entry_id + ".md":
                return entry_id
        return None

    def resolve(self, label: str, path_part: str) -> Path | None:
        """返回相对 正文/ 的目标路径；无法唯一确定时返回 None。"""
        label = label.strip()
        basename = Path(path_part.replace("\\", "/")).name
        candidates: list[Path] = []

        if label in self.id_to_path:
            candidates = [self.id_to_path[label]]

        if not candidates and basename:
            fid = self.id_from_filename(basename)
            if fid and fid in self.id_to_path:
                candidates = [self.id_to_path[fid]]

        if not candidates and basename in self.by_name:
            names = self.by_name[basename]
            if len(names) == 1:
                candidates = [Path(names[0])]

        if not candidates and basename:
            norm = path_part.replace("\\", "/").lstrip("./")
            for rel in self.by_name.get(basename, []):
                if rel.endswith(norm) or norm.endswith(rel):
                    candidates.append(Path(rel))

        if not candidates:
            return None

        uniq = list(dict.fromkeys(candidates))
        if len(uniq) == 1:
            return uniq[0]
        return None


def relpath_link(from_file: Path, to_rel: Path, anchor: str = "") -> str:
    target = (from_file.parent / to_rel).resolve()
    rel = os.path.relpath(target, from_file.parent).replace("\\", "/")
    return rel + anchor


def line_number_at(raw: str, pos: int) -> int:
    return raw.count("\n", 0, pos) + 1


def scan_links(
    root: Path,
) -> tuple[
    list[tuple[str, int, str, str]],
    list[tuple[str, int, str]],
    int,
]:
    broken: list[tuple[str, int, str, str]] = []
    malformed: list[tuple[str, int, str]] = []
    ok = 0

    for md in sorted(root.rglob("*.md")):
        raw = md.read_text(encoding="utf-8")
        forbidden = forbidden_ranges(raw)
        rel = str(md.relative_to(root))

        for m in MALFORMED_RE.finditer(raw):
            if pos_forbidden(m.start(), forbidden):
                continue
            malformed.append((rel, line_number_at(raw, m.start()), m.group(0)))

        for m in LINK_RE.finditer(raw):
            if pos_forbidden(m.start(), forbidden):
                continue
            target = m.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part, _, _anchor = target.partition("#")
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                broken.append((rel, line_number_at(raw, m.start()), target, m.group(0)))
            else:
                ok += 1

    return broken, malformed, ok


def scan_registry(root: Path) -> tuple[list[str], set[str]]:
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


def fix_malformed_in_text(text: str) -> tuple[str, int]:
    n = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        return f"[{m.group(1)}]({m.group(2)}{m.group(3)})"

    return MALFORMED_RE.subn(repl, text)[0], n


def fix_links_in_file(md: Path, root: Path, index: LinkIndex) -> int:
    text = md.read_text(encoding="utf-8")
    forbidden = forbidden_ranges(text)
    fixes: list[tuple[int, int, str]] = []
    n = 0

    for m in LINK_RE.finditer(text):
        if pos_forbidden(m.start(), forbidden):
            continue
        label, target = m.group(1), m.group(2).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part, sep, anchor_suffix = target.partition("#")
        if not path_part:
            continue
        resolved = (md.parent / path_part).resolve()
        if resolved.exists():
            continue

        anchor = sep + anchor_suffix if sep else ""
        to_rel = index.resolve(label, path_part)
        if to_rel is None:
            continue

        new_target = relpath_link(md, to_rel, anchor)
        if new_target == target:
            continue

        if m.group(0).startswith("!"):
            new_link = f"![{label}]({new_target})"
        else:
            new_link = f"[{label}]({new_target})"

        fixes.append((m.start(), m.end(), new_link))
        n += 1

    if not fixes:
        return 0

    fixes.sort(key=lambda x: x[0], reverse=True)
    for start, end, repl in fixes:
        text = text[:start] + repl + text[end:]
    md.write_text(text, encoding="utf-8")
    return n


def run_auto_fix(root: Path) -> tuple[int, list[str]]:
    registry = load_registry(root)
    index = LinkIndex(root, registry)
    log: list[str] = []
    total = 0

    for md in sorted(root.rglob("*.md")):
        raw = md.read_text(encoding="utf-8")
        new_raw, n_mal = fix_malformed_in_text(raw)
        if n_mal:
            md.write_text(new_raw, encoding="utf-8")
            log.append(f"  {md.relative_to(root)}：畸形链接 {n_mal} 处")
            total += n_mal

        n_link = fix_links_in_file(md, root, index)
        if n_link:
            log.append(f"  {md.relative_to(root)}：重定向链接 {n_link} 处")
            total += n_link

    return total, log


def stage_fixed_files(root: Path, repo: Path) -> None:
    rel_root = root.relative_to(repo).as_posix()
    subprocess.run(
        ["git", "add", "--", rel_root],
        cwd=repo,
        check=False,
    )


def print_issues(
    malformed: list[tuple[str, int, str]],
    broken: list[tuple[str, int, str, str]],
    reg_issues: list[str],
    manifest_issues: list[str],
) -> None:
    if malformed:
        print(f"畸形链接（缺 ]( ）：{len(malformed)}")
        for rel, line, snippet in malformed:
            print(f"  {rel}:{line}\n    {snippet}")

    if broken:
        print(f"断链（无法自动修复）：{len(broken)}")
        for rel, line, target, snippet in broken:
            print(f"  {rel}:{line}\n    目标: {target}\n    {snippet}")

    if reg_issues:
        print(f"注册表路径问题：{len(reg_issues)}")
        for msg in reg_issues:
            print(f"  {msg}")

    if manifest_issues:
        print(f"manifest 登记问题：{len(manifest_issues)}")
        for msg in manifest_issues:
            print(f"  {msg}")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验正文 Markdown 内部链接与登记一致性")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="按文件名 / 注册表 id 自动修正断链与畸形链接，然后重新校验",
    )
    parser.add_argument(
        "--stage-fixed",
        action="store_true",
        help="与 --fix 联用：将正文/ 下已修改文件执行 git add（纳入本次提交，不 push）",
    )
    parser.add_argument(
        "--fix-malformed",
        action="store_true",
        help="（已并入 --fix）仅修复缺 ]( 的畸形链接",
    )
    args = parser.parse_args()

    root = canon_root()
    if not root.is_dir():
        print(f"找不到正文目录：{root}", file=sys.stderr)
        return 1

    do_fix = args.fix or args.fix_malformed

    if do_fix:
        total, log = run_auto_fix(root)
        if log:
            print(f"已自动修正 {total} 处：")
            print("\n".join(log))
        if args.stage_fixed:
            stage_fixed_files(root, repo_root())
            print("已将 正文/ 下变更加入暂存区（git add）。")

    broken, malformed, ok = scan_links(root)
    reg_issues, registry_ids = scan_registry(root)
    manifest_issues = scan_manifest(root, registry_ids)

    total_bad = len(broken) + len(malformed) + len(reg_issues) + len(manifest_issues)
    if total_bad:
        print()
        print_issues(malformed, broken, reg_issues, manifest_issues)
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
