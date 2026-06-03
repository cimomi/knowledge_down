#!/usr/bin/env python3
"""知识库构建脚本（仅用标准库）。

entries/*.md  --(解析 frontmatter + 正文)-->  manifest.json
                                          --(注入 template.html)-->  index.html

设计要点：扫描与生成都在本子进程完成，输出极小，不需要把库内容读进 agent 上下文。
无第三方依赖，沙盒/任意机器可直接 `python3 build.py` 运行。
"""
import json, os, re, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRIES = ROOT / "entries"
TEMPLATE = ROOT / "template.html"
OUT = ROOT / "index.html"
MANIFEST = ROOT / "manifest.json"


def parse_frontmatter(text: str):
    """极简 YAML frontmatter 解析：支持 key: value 与 key: [a, b] 列表。"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        else:
            meta[key] = val.strip("'\"")
    return meta, body


def main():
    entries = []
    if ENTRIES.exists():
        for f in sorted(ENTRIES.glob("*.md")):
            meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
            tags = meta.get("tags", [])
            if isinstance(tags, str):
                tags = [tags] if tags else []
            entries.append({
                "id": meta.get("id", f.stem),
                "title": meta.get("title", f.stem),
                "date": meta.get("date", ""),
                "type": meta.get("type", "未分类"),
                "tags": tags,
                "source": meta.get("source", ""),
                "summary": meta.get("summary", ""),
                "file": f"entries/{f.name}",
                "body": body,
            })
    entries.sort(key=lambda e: (e.get("date", ""), e.get("id", "")), reverse=True)

    manifest = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "count": len(entries),
        "types": sorted({e["type"] for e in entries}),
        "tags": sorted({t for e in entries for t in e["tags"]}),
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if TEMPLATE.exists():
        tpl = TEMPLATE.read_text(encoding="utf-8")
        # 注入到 <script type="application/json" id="kb-data">__KB_DATA__</script>
        data = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
        OUT.write_text(tpl.replace("__KB_DATA__", data), encoding="utf-8")
        print(f"[build] {len(entries)} entries -> {OUT.name}  (types={len(manifest['types'])}, tags={len(manifest['tags'])})")
    else:
        print(f"[build] manifest.json written ({len(entries)} entries). template.html 缺失，已跳过 index.html。")


if __name__ == "__main__":
    main()
