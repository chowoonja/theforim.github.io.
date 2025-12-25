import os
import urllib.parse
from bs4 import BeautifulSoup

TREE_DIR = "trees"

FORM_BASE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdgujOIV9bKAUyOAot7AoysT4UWBrrIKkQbIgWirDtZjaapQA/viewform"

# ✅ 네가 준 “자동입력 되는” entry 번호로 확정
ENTRY_PARK = "entry.1291403664"   # 공원명
ENTRY_TREE = "entry.1870322508"   # 수목코드

PARK_NAME = "복하천 제2수변공원"

def make_prefill_url(tree_code: str) -> str:
    params = {
        ENTRY_PARK: PARK_NAME,
        ENTRY_TREE: tree_code,
    }
    # usp=pp_url 없어도 네 링크처럼 entry만으로 자동입력 됨
    return FORM_BASE_URL + "?" + urllib.parse.urlencode(params)

patched = 0

for fn in os.listdir(TREE_DIR):
    if not fn.startswith("B2-") or not fn.endswith(".html"):
        continue

    tree_code = fn[:-5]
    path = os.path.join(TREE_DIR, fn)

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    target = make_prefill_url(tree_code)
    changed = False

    # '조사 기록' 버튼(<a>) 링크 교체
    for a in soup.find_all("a"):
        if a.get_text(" ", strip=True) == "조사 기록":
            a["href"] = target
            a["target"] = "_blank"
            changed = True

    # 혹시 <button onclick>이면 이것도 교체
    for b in soup.find_all("button"):
        if b.get_text(" ", strip=True) == "조사 기록":
            b["onclick"] = f"window.open('{target}','_blank')"
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        patched += 1

print(f"✅ 조사 기록 버튼 자동입력 링크 적용: {patched}개")