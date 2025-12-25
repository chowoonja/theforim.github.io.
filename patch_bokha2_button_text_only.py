import os
from bs4 import BeautifulSoup

TREE_DIR = "trees"

count = 0
for fn in os.listdir(TREE_DIR):
    if not fn.startswith("B2-") or not fn.endswith(".html"):
        continue

    path = os.path.join(TREE_DIR, fn)
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    changed = False
    for tag in soup.find_all(["a", "button"]):
        txt = tag.get_text(" ", strip=True)
        if "조사기록 입력" in txt or "조사기록" == txt or "관리 기록" in txt or "기록 입력" in txt:
            tag.string = "조사 기록"
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        count += 1

print(f"✅ 버튼 텍스트 변경 완료: {count}개")