"""HTML本文に含まれる \\uXXXX エスケープを実Unicode文字に変換する汎用スクリプト。

対象ファイルを引数で複数受け取れる。サロゲートペア（絵文字 U+10000以上）
にも対応。JS文字列内の \\uXXXX も同時に変換されるが、機能差は無い
（\"\\u5473\\u899A\" と \"味覚\" は JS で同等）。

使い方:
    python _fix_unicode_escapes.py <file1.html> [file2.html ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

ESCAPE_RE = re.compile(r"\\u([0-9A-Fa-f]{4})")
SURROGATE_PAIR_RE = re.compile(
    r"\\u(D[89ABab][0-9A-Fa-f]{2})\\u(D[CDEFcdef][0-9A-Fa-f]{2})"
)


def decode_surrogate_pair(m: re.Match) -> str:
    high = int(m.group(1), 16)
    low = int(m.group(2), 16)
    code_point = ((high - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
    return chr(code_point)


def fix_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    before_size = len(text)
    escape_count = len(ESCAPE_RE.findall(text))
    if escape_count == 0:
        print(f"  {path.name}: スキップ（エスケープ無し）")
        return
    text = SURROGATE_PAIR_RE.sub(decode_surrogate_pair, text)
    new_text = ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), text)
    after_size = len(new_text)
    remain = len(ESCAPE_RE.findall(new_text))
    path.write_text(new_text, encoding="utf-8", newline="\n")
    print(
        f"  {path.name}: {escape_count}件置換 / "
        f"{before_size:,}→{after_size:,} bytes / 残存{remain}件"
    )


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python _fix_unicode_escapes.py <file1> [file2 ...]")
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_absolute():
            path = Path(__file__).parent / arg
        if not path.exists():
            print(f"  {arg}: ファイルが見つかりません", file=sys.stderr)
            continue
        fix_file(path)


if __name__ == "__main__":
    main()
