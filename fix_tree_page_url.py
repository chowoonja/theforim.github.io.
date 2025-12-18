# -*- coding: utf-8 -*-
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 수정 대상 폴더들 (필요하면 추가)
TARGET_DIRS = [
    os.path.join(BASE_DIR, "parks", "안흥유원지", "trees"),
    os.path.join(BASE_DIR, "trees"),
]

# 페이지 URL을 올바른 경로로 통일하기 위한 함수
def correct_page_url(file_name: str, dir_path: str) -> str:
    # parks/안흥유원지/trees 아래면 해당 경로로
    if os.path.normpath(dir_path).endswith(os.path.normpath(os.path.join("parks", "안흥유원지", "trees"))):
        return f"https://theforim.com/parks/안흥유원지/trees/{file_name}"
    # 루트 trees 아래면 /trees/
    return f"https://theforim.com/trees/{file_name}"

def main():
    total = 0
    changed = 0
    not_found = 0

    # "페이지 URL:" 라인을 찾아 교체 (HTML 구조가 조금 달라도 잡히게 느슨하게)
    # 예: 페이지 URL: https://theforim.com/trees/DT0004.html
    url_pattern = re.compile(r'(페이지\s*URL\s*:\s*)(https?://[^\s<]+)', re.IGNORECASE)

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

            if url_pattern.search(html):
                new_html = url_pattern.sub(rf"\1{new_url}", html, count=1)
                if new_html != html:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_html)
                    changed += 1
            else:
                not_found += 1

    print("=== fix_tree_page_url 결과 ===")
    print(f"대상 파일 수: {total}")
    print(f"수정됨(페이지 URL 교체): {changed}")
    print(f"'페이지 URL' 패턴 못 찾음: {not_found}")

if __name__ == "__main__":
    main()