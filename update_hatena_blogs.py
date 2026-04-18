"""
はてなブログの8記事にセルフチェックツールへのリンクを追加

ローカルHTMLからbody部分を抽出し、AtomPub APIで更新する
"""
import os, sys, re, base64, requests
from pathlib import Path
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BLOG_DIR = Path(r"C:\Users\jsber\OneDrive\Documents\Claude_task\blog\general-series")
HATENA_ID = "hinyan1016"
BLOG_DOMAIN = "hinyan1016.hatenablog.com"
API_KEY = os.environ.get("HATENA_API_KEY", "y8n4v3sioq")
TOOL_BASE_URL = "https://hinyan1016.github.io/symptom-checker"

NS = {'atom': 'http://www.w3.org/2005/Atom', 'app': 'http://www.w3.org/2007/app'}

# (ブログファイル, はてなedit URL, ツールファイル名)
ENTRIES = [
    ("01_forgetfulness_vs_dementia_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901371557759",
     "forgetfulness-check.html"),
    ("03_hand_numbness_morning_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901371583924",
     "hand-numbness-morning-check.html"),
    ("04_vertigo_types_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901371583942",
     "dizziness-type-check.html"),
    ("05_functional_neurological_disorder_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901371583952",
     "fnd-awareness-check.html"),
    ("13_dangerous_headache_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901372000521",
     "headache-danger-check.html"),
    ("14_numbness_which_department_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901372000527",
     "numbness-dept-check.html"),
    ("15_frequent_tripping_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901372000531",
     "stumbling-check.html"),
    ("16_seizure_first_aid_blog.html",
     "https://blog.hatena.ne.jp/hinyan1016/hinyan1016.hatenablog.com/atom/entry/17179246901372000539",
     "seizure-response-check.html"),
]


def extract_body(html):
    """HTMLからbody内容を抽出（<style>ブロック除去、<body>タグ除去）"""
    # <body>...</body> を抽出
    m = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL | re.IGNORECASE)
    if m:
        body = m.group(1).strip()
    else:
        body = html

    # <style>ブロック除去
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)

    # <!DOCTYPE ...> 除去
    body = re.sub(r'<!DOCTYPE[^>]*>', '', body, flags=re.IGNORECASE)

    return body.strip()


def get_entry(edit_url):
    """既存エントリを取得"""
    resp = requests.get(edit_url, auth=(HATENA_ID, API_KEY))
    if resp.status_code != 200:
        print(f"  GET失敗: {resp.status_code}")
        return None
    return resp.text


def check_already_has_link(entry_xml, tool_file):
    """既にツールリンクがあるかチェック"""
    tool_url = f"{TOOL_BASE_URL}/{tool_file}"
    return tool_url in entry_xml


def update_entry(edit_url, entry_xml, new_body):
    """エントリのcontent部分をnew_bodyに置換してPUT"""
    root = ET.fromstring(entry_xml)

    # content要素を更新
    content_el = root.find('atom:content', NS)
    if content_el is None:
        print("  content要素が見つかりません")
        return False

    content_el.text = new_body
    content_el.set('type', 'text/html')

    # XML出力
    ET.register_namespace('', 'http://www.w3.org/2005/Atom')
    ET.register_namespace('app', 'http://www.w3.org/2007/app')
    updated_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)

    resp = requests.put(
        edit_url,
        data=updated_xml.encode('utf-8'),
        auth=(HATENA_ID, API_KEY),
        headers={'Content-Type': 'application/atom+xml; charset=utf-8'}
    )

    if resp.status_code == 200:
        return True
    else:
        print(f"  PUT失敗: {resp.status_code}")
        return False


def main():
    updated = 0
    skipped = 0

    for blog_file, edit_url, tool_file in ENTRIES:
        print(f"\n処理中: {blog_file}")

        # 既存エントリ取得
        entry_xml = get_entry(edit_url)
        if entry_xml is None:
            continue

        # 既にリンクがあればスキップ
        if check_already_has_link(entry_xml, tool_file):
            print(f"  [SKIP] ツールリンク既存")
            skipped += 1
            continue

        # ローカルHTMLからbody抽出
        local_path = BLOG_DIR / blog_file
        local_html = local_path.read_text(encoding='utf-8')
        new_body = extract_body(local_html)

        # 更新
        if update_entry(edit_url, entry_xml, new_body):
            print(f"  [OK] 更新成功")
            updated += 1
        else:
            print(f"  [FAIL] 更新失敗")

    print(f"\n完了: 更新{updated}件, スキップ{skipped}件")


if __name__ == "__main__":
    main()
