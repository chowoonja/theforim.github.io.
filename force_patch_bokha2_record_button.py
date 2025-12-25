import os
import urllib.parse
from bs4 import BeautifulSoup

TREE_DIR = "trees"

FORM_BASE = "https://docs.google.com/forms/d/e/1FAIpQLSdgujOIV9bKAUyOAot7AoysT4UWBrrIKkQbIgWirDtZjaapQA/viewform"
ENTRY_PARK = "entry.1291403664"   # 공원명
ENTRY_TREE = "entry.1870322508"   # 수목코드
PARK_NAME = "복하천 제2수변공원"

def make_url(tree_code: str) -> str:
    params = {
        "usp": "pp_url",
        ENTRY_PARK: PARK_NAME,
        ENTRY_TREE: tree_code,
    }
    return FORM_BASE + "?" + urllib.parse.urlencode(params)
patched = 0
missed = []

for fn in os.listdir(TREE_DIR):
    if not fn.startswith("B2-") or not fn.endswith(".html"):
        continue

    tree_code = fn[:-5]
    path = os.path.join(TREE_DIR, fn)

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    target = make_url(tree_code)
    changed = False
    found_button = False

    # 1) <a> 태그 중: class에 btn-old-record 있거나, 텍스트에 '조사'+'기록' 포함이면 무조건 교체
    for a in soup.find_all("a"):
        txt = a.get_text(" ", strip=True)
        cls = " ".join(a.get("class", []))
        if ("btn-old-record" in cls) or ("조사" in txt and "기록" in txt):
            a["href"] = target
            a["target"] = "_blank"
            found_button = True
            changed = True

    # 2) <button>도 동일하게 처리 (onclick 강제)
    for b in soup.find_all("button"):
        txt = b.get_text(" ", strip=True)
        cls = " ".join(b.get("class", []))
        if ("btn-old-record" in cls) or ("조사" in txt and "기록" in txt):
            b["onclick"] = f"window.open('{target}','_blank')"
            found_button = True
            changed = True

    # 3) 혹시 onclick 안에 폼 링크가 박혀있으면 그것도 무조건 교체
    for tag in soup.find_all(True):
        onclick = tag.get("onclick", "")
        if "docs.google.com/forms" in onclick or "forms.gle" in onclick:
            tag["onclick"] = f"window.open('{target}','_blank')"
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        patched += 1

    if not found_button:
        missed.append(fn)

print(f"✅ 강제 패치 완료: {patched}개")
print(f"⚠️ 버튼을 못 찾은 파일 수: {len(missed)}")
if missed[:10]:
    print("예시(앞 10개):", ", ".join(missed[:10]))