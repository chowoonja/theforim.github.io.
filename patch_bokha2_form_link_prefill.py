import os
import urllib.parse
from bs4 import BeautifulSoup

TREE_DIR = "trees"

FORM_BASE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdgujOIV9bKAUyOAot7AoysT4UWBrrIKkQbIgWirDtZjaapQA/viewform"

ENTRY_PARK = "entry.939121262"   # 공원명
ENTRY_TREE = "entry.253024248"   # 수목코드

PARK_NAME = "복하천 제2수변공원"

def make_prefill_url(tree_code: str) -> str:
    params = {
        "usp": "pp_url",
        ENTRY_PARK: PARK_NAME,
        ENTRY_TREE: tree_code,
    }
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

    # 1) <a> 버튼 케이스
    for a in soup.find_all("a"):
        if a.get_text(" ", strip=True) == "조사 기록":
            a["href"] = target
            a["target"] = "_blank"
            changed = True

    # 2) <button onclick> 케이스(혹시 있을 때)
    for b in soup.find_all("button"):
        if b.get_text(" ", strip=True) == "조사 기록":
            b["onclick"] = f"window.open('{target}','_blank')"
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        patched += 1

print(f"✅ 조사기록 버튼 미리채움 링크 적용: {patched}개")