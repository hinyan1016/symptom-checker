"""
からだの不思議シリーズ：ブログ ↔ セルフチェックツール相互リンク追加スクリプト

1. ブログHTML → セルフチェックツールへのリンクを追加
2. セルフチェックツールHTML → ブログ記事へのリンクを追加
"""
import re
from pathlib import Path

BLOG_DIR = Path(r"C:\Users\jsber\OneDrive\Documents\Claude_task\blog\general-series")
TOOL_DIR = Path(r"C:\Users\jsber\OneDrive\Documents\Claude_task\symptom-checker")
TOOL_BASE_URL = "https://hinyan1016.github.io/symptom-checker"

# 対応表: (ブログファイル, ツールファイル, はてなURL, シリーズ番号, ブログタイトル, ツールタイトル)
MAPPINGS = [
    ("01_forgetfulness_vs_dementia_blog.html", "forgetfulness-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/01/230038",
     "#1", "「あの人の名前が出てこない」は認知症のサインか？", "物忘れセルフチェック"),
    ("03_hand_numbness_morning_blog.html", "hand-numbness-morning-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/03/214301",
     "#3", "「手がしびれて目が覚めた」の正体", "朝の手しびれセルフチェック"),
    ("04_vertigo_types_blog.html", "dizziness-type-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/05/045104",
     "#4", "めまいの種類を脳神経内科医が解説", "めまい分類セルフチェック"),
    ("05_functional_neurological_disorder_blog.html", "fnd-awareness-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/05/081707",
     "#5", "ストレスで本当に体は動かなくなるのか", "ストレスと体の症状セルフチェック"),
    ("13_dangerous_headache_blog.html", "headache-danger-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/13/182624",
     "#13", "この頭痛、病院に行くべき？", "危険な頭痛セルフチェック"),
    ("14_numbness_which_department_blog.html", "numbness-dept-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/14/200622",
     "#14", "しびれが出たら何科？", "しびれ受診科セルフチェック"),
    ("15_frequent_tripping_blog.html", "stumbling-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/15/104135",
     "#15", "「最近つまずきやすい」は脳の問題？", "つまずきセルフチェック"),
    ("16_seizure_first_aid_blog.html", "seizure-response-check.html",
     "https://hinyan1016.hatenablog.com/entry/2026/04/15/135014",
     "#16", "けいれんを目撃したときの正しい対応", "けいれん対応セルフチェック"),
]


def add_tool_link_to_blog(blog_file, tool_file, tool_title):
    """ブログ記事にセルフチェックツールへのリンクを追加"""
    path = BLOG_DIR / blog_file
    html = path.read_text(encoding="utf-8")

    tool_url = f"{TOOL_BASE_URL}/{tool_file}"

    # 既にリンクがあればスキップ
    if tool_url in html or tool_file in html:
        print(f"  [SKIP] {blog_file}: ツールリンク既存")
        return False

    # セルフチェックツールのリンクブロック
    link_block = (
        '<div style="background:#e8f4fd;border-left:4px solid #2C5AA0;'
        'padding:16px 20px;margin:24px 0;border-radius:4px;">'
        '<p style="margin:0 0 8px;font-weight:bold;color:#1B3A5C;">'
        '\U0001f4cb セルフチェックツール</p>'
        '<p style="margin:0;font-size:0.95em;color:#333;">'
        f'この記事の内容をもとにした無料セルフチェックツールです。'
        f'6つの質問に答えるだけで、受診の目安がわかります。</p>'
        f'<p style="margin:8px 0 0;"><a href="{tool_url}" '
        f'target="_blank" rel="noopener" '
        f'style="color:#2C5AA0;font-weight:bold;text-decoration:underline;">'
        f'\u25B6 {tool_title}を試す</a></p>'
        '</div>'
    )

    # 挿入位置: 参考文献/関連記事の直前、または</body>の前
    # パターン1: <div class="references"> or ref-section
    # パターン2: <div class="related-box"> or 関連記事
    # パターン3: </body>
    for pattern in [
        r'(<div[^>]*class="references"[^>]*>)',
        r'(<div[^>]*class="ref-section"[^>]*>)',
        r'(<div[^>]*>\s*<h[23][^>]*>\s*参考文献)',
        r'(<div[^>]*style="[^"]*background[^"]*#[^"]*"[^>]*>\s*<p[^>]*>\s*<strong>\s*参考文献)',
        r'(<div[^>]*style="[^"]*background[^"]*#[^"]*"[^>]*>\s*<p[^>]*>\s*<strong>\s*関連記事)',
        r'(</body>)',
    ]:
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if m:
            insert_pos = m.start()
            html = html[:insert_pos] + link_block + "\n\n" + html[insert_pos:]
            path.write_text(html, encoding="utf-8")
            print(f"  [OK] {blog_file}: ツールリンク追加")
            return True

    print(f"  [WARN] {blog_file}: 挿入位置が見つかりません")
    return False


def add_blog_link_to_tool(tool_file, hatena_url, blog_title, series_num):
    """セルフチェックツールにブログ記事へのリンクを追加"""
    path = TOOL_DIR / tool_file
    html = path.read_text(encoding="utf-8")

    # 既にリンクがあればスキップ
    if hatena_url in html or "blog-link" in html:
        print(f"  [SKIP] {tool_file}: ブログリンク既存")
        return False

    # リンクブロック: disclaimer の後に挿入
    link_block = (
        '<div class="blog-link" style="background:#e8f4fd;border-left:4px solid #2C5AA0;'
        'padding:10px 16px;margin:0 16px 0;border-radius:4px;font-size:0.85rem;">'
        f'\U0001f4d6 <a href="{hatena_url}" target="_blank" rel="noopener" '
        f'style="color:#2C5AA0;text-decoration:underline;">'
        f'ブログ記事「{blog_title}」で詳しく解説</a>'
        '</div>'
    )

    # disclaimer の直後に挿入
    disclaimer_pattern = r'(</div>\s*\n)(\s*<div class="progress-bar")'
    m = re.search(disclaimer_pattern, html)
    if m:
        html = html[:m.end(1)] + link_block + "\n" + html[m.start(2):]
        path.write_text(html, encoding="utf-8")
        print(f"  [OK] {tool_file}: ブログリンク追加")
        return True

    print(f"  [WARN] {tool_file}: 挿入位置が見つかりません")
    return False


def main():
    print("=== ブログ → セルフチェックツール リンク追加 ===")
    blog_count = 0
    for blog_file, tool_file, _, _, _, tool_title in MAPPINGS:
        if add_tool_link_to_blog(blog_file, tool_file, tool_title):
            blog_count += 1

    print(f"\n=== セルフチェックツール → ブログ リンク追加 ===")
    tool_count = 0
    for _, tool_file, hatena_url, series_num, blog_title, _ in MAPPINGS:
        if add_blog_link_to_tool(tool_file, hatena_url, blog_title, series_num):
            tool_count += 1

    print(f"\n完了: ブログ {blog_count}件, ツール {tool_count}件 更新")


if __name__ == "__main__":
    main()
