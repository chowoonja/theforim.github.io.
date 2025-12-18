# -*- coding: utf-8 -*-
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TARGET_DIRS = [
    os.path.join(BASE_DIR, "parks", "안흥유원지", "trees"),
    os.path.join(BASE_DIR, "trees"),
]

def correct_page_url(file_name: str, dir_path: str) -> str:
    if os.path.normpath(dir_path).endswith(os.path.normpath(os.path.join("parks", "안흥유원지", "trees"))):
        return f"https://theforim.com/parks/안흥유원지/trees/{file_name}"
    return f"https://theforim.com/trees/{file_name}"

def main():
    total = changed = not_found = 0

    # ✅ "페이지 URL"이 포함된 문단/줄 안에서 <code>...</code> 를 찾아 그 안의 URL만 교체
    # (태그/줄바꿈 섞여도 잡히도록 DOTALL)
    block_pat = re.compile(r"(페이지\s*URL[\s:：]*.*?</p>)", re.IGNORECASE | re.DOTALL)
    code_url_pat = re.compile(r"(<code>\s*)(https?://[^<\s]+)(\s*</code>)", re.IGNORECASE)

    for target in TARGET_DIRS:
        if not os.path.isdir(target):
            continue

        for fn in sorted(os.listdir(target)):
            if not (fn.startswith("DT") and fn.endswith(".html")):
                continue

            total += 1
            path = os.path.join(target, fn)

            with open(path, "r", encoding="utf-8") as f:
                html = f.read()

            new_url = correct_page_url(fn, target)

            # 1) 페이지 URL이 들어있는 p블록을 찾는다
            m = block_pat.search(html)
            if not m:
                not_found += 1
                continue

            block = m.group(1)

            # 2) 그 블록 안의 <code>URL</code> 만 바꾼다
            new_block, n = code_url_pat.subn(rf"\1{new_url}\3", block, count=1)
            if n == 0:
                not_found += 1
                continue

            new_html = html[:m.start(1)] + new_block + html[m.end(1):]

            if new_html != html:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_html)
                changed += 1

    print("=== fix_tree_page_url_v2 결과 ===")
    print(f"대상 파일 수: {total}")
    print(f"수정됨(페이지 URL 교체): {changed}")
    print(f"못 찾음(페이지 URL 블록/코드): {not_found}")

if __name__ == "__main__":
    main()