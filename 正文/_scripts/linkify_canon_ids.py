# -*- coding: utf-8 -*-
"""将正文 Markdown 中已注册的设定 id（WLD/ORG/PLC/SYS/ENT/NAR）转为相对路径链接。"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")


def load_registry(registry_path: Path) -> dict[str, str]:
    text = registry_path.read_text(encoding="utf-8")
    entries: dict[str, str] = {}
    for block in text.split("\n  - id: ")[1:]:
        id_line = block.split("\n", 1)[0].strip()
        m_path = re.search(r"^\s*path:\s*(.+\.md)\s*$", block, re.MULTILINE)
        if m_path and id_line:
            entries[id_line] = m_path.group(1).strip()
    return entries


def split_frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"^---\n[\s\S]*?\n---\n", text)
    if m:
        return m.group(0), text[m.end() :]
    return "", text


def iter_link_chunks(s: str):
    pos = 0
    for m in LINK_RE.finditer(s):
        if m.start() > pos:
            yield False, s[pos : m.start()]
        yield True, m.group(0)
        pos = m.end()
    if pos < len(s):
        yield False, s[pos:]


def rel_href(from_file: Path, root: Path, target_rel: str) -> str:
    target = root / target_rel
    return os.path.relpath(target, from_file.parent).replace("\\", "/")


def linkify_chunk(chunk: str, from_file: Path, root: Path, ids_sorted: list[str], id_map: dict[str, str]) -> str:
    for cid in ids_sorted:
        href = rel_href(from_file, root, id_map[cid])
        chunk = re.sub(
            r"`" + re.escape(cid) + r"`",
            f"[{cid}]({href})",
            chunk,
        )

    for cid in ids_sorted:
        href = rel_href(from_file, root, id_map[cid])

        def repl(m: re.Match[str]) -> str:
            start = m.start()
            if start > 0 and chunk[start - 1] == "[":
                end = m.end()
                if chunk[end : end + 2] == "](":
                    return m.group(0)
            return f"[{cid}]({href})"

        # 避免匹配更长文件名前缀（如 ORG-HELIOS-赫利俄斯.md 中的 ORG-HELIOS）
        chunk = re.sub(r"\b" + re.escape(cid) + r"\b(?!-)", repl, chunk)
    return chunk


def linkify_outside_links(text: str, from_file: Path, root: Path, ids_sorted: list[str], id_map: dict[str, str]) -> str:
    out = []
    for is_link, chunk in iter_link_chunks(text):
        if is_link:
            out.append(chunk)
        else:
            out.append(linkify_chunk(chunk, from_file, root, ids_sorted, id_map))
    return "".join(out)


def linkify_body(body: str, from_file: Path, root: Path, ids_sorted: list[str], id_map: dict[str, str]) -> str:
    parts = re.split(r"(```[\s\S]*?```)", body)
    result = []
    for i, part in enumerate(parts):
        if part.startswith("```"):
            result.append(part)
        else:
            result.append(linkify_outside_links(part, from_file, root, ids_sorted, id_map))
    return "".join(result)


def resolve_zhengwen_root() -> Path:
    """定位「正文」根目录：支持在仓库根执行，或在正文目录内执行。"""
    cwd = Path.cwd().resolve()
    for base in (cwd, *cwd.parents):
        nested = base / "正文" / "治理" / "id-registry.yaml"
        if nested.is_file():
            return nested.parent.parent.resolve()
        direct = base / "治理" / "id-registry.yaml"
        if direct.is_file() and (base / "设定真值").is_dir():
            return base.resolve()
    raise SystemExit(
        "找不到正文注册表：请在仓库根目录执行 "
        "`python 正文/_scripts/linkify_canon_ids.py`（正文内含 治理/id-registry.yaml）。"
    )


def main() -> int:
    root = resolve_zhengwen_root()
    registry = root / "治理" / "id-registry.yaml"
    id_map = load_registry(registry)
    ids_sorted = sorted(id_map.keys(), key=len, reverse=True)

    changed = 0
    for md in sorted(root.rglob("*.md")):
        if md.name == "README.md" and md.parent == root:
            pass
        rel_self = md.relative_to(root)
        if rel_self.parts[:1] == ("_scripts",):
            continue

        raw = md.read_text(encoding="utf-8")
        fm, body = split_frontmatter(raw)
        new_body = linkify_body(body, md, root, ids_sorted, id_map)
        new_raw = fm + new_body
        if new_raw != raw:
            md.write_text(new_raw, encoding="utf-8", newline="\n")
            changed += 1
            print("updated:", md.relative_to(root))

    print("done, files changed:", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
