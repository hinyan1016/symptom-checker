"""HTML本文に \\uXXXX エスケープが含まれているツールを検出する監査スクリプト。

JS文字列リテラル内の \\uXXXX は正しく動作する（文字化けしない）が、
HTML本文（タグの内側のテキスト）に書かれた \\uXXXX はブラウザで
そのまま文字として表示され文字化けの原因になる。

本スクリプトは <script>...</script> ブロックを除いた HTML 本文部分のみを
対象に \\uXXXX の出現を数え、修正対象ファイルを特定する。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

ROOT = Path(r"C:\Users\jsber\OneDrive\Documents\Claude_task_new\symptom-checker")

ESCAPE_RE = re.compile(r"\\u[0-9A-Fa-f]{4}")
SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)
STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.DOTALL | re.IGNORECASE)


def analyze(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    total = len(ESCAPE_RE.findall(text))
    # script/style ブロックを除外した「HTML本文」を抽出
    body_only = SCRIPT_BLOCK_RE.sub("", text)
    body_only = STYLE_BLOCK_RE.sub("", body_only)
    body_escapes = len(ESCAPE_RE.findall(body_only))
    in_script = total - body_escapes
    return {
        "file": path.name,
        "total_escapes": total,
        "html_body_escapes": body_escapes,
        "in_script_or_style": in_script,
        "needs_fix": body_escapes > 0,
    }


def main() -> None:
    results = []
    for f in sorted(ROOT.glob("*.html")):
        results.append(analyze(f))

    print(f"{'File':<40} {'TotalEsc':>9} {'HTMLbody':>9} {'JSstr':>7} Fix?")
    print("-" * 75)
    needs_fix = []
    for r in results:
        flag = "🔴 FIX" if r["needs_fix"] else "  ok"
        print(
            f"{r['file']:<40} {r['total_escapes']:>9} "
            f"{r['html_body_escapes']:>9} {r['in_script_or_style']:>7} {flag}"
        )
        if r["needs_fix"]:
            needs_fix.append(r["file"])

    print("-" * 75)
    print(f"修正対象（HTML本文にエスケープあり）: {len(needs_fix)}件")
    for name in needs_fix:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
