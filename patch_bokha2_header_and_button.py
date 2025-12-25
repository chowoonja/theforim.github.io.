import os
import pandas as pd
from bs4 import BeautifulSoup

XLSX = "Bokha2_trees.xlsx"
TREE_DIR = "trees"
PARK_NAME = "복하천제2수변공원"

df = pd.read_excel(XLSX)
df.columns = [str(c).strip() for c in df.columns]

def v(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

# 복하천 대상 코드만
codes = []
for _, row in df.iterrows():
    code = v(row.get("수목코드", ""))
    url = v(row.get("QR_URL", ""))
    if code.startswith("B2-") and url.startswith("http"):
        codes.append(code)

def replace_text_in_tag(tag, old, new):
    if tag and tag.string:
        tag.string = tag.string.replace(old, new)

patched = 0

for code in codes:
    path = os.path.join(TREE_DIR, f"{code}.html")
    if not os.path.exists(path):
        continue

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 1) <title> 교체 (DT0001/안흥유원지 흔적 제거)
    title = soup.find("title")
    if title:
        title.string = f"{code} · {PARK_NAME} · THE FORIM"

    # 2) 헤더의 "조사번호: DT0001 · 안흥유원지" 같은 문구 교체
    #    (p 태그들 중 '조사번호:' 포함된 것을 찾아 통째로 바꿈)
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        if "조사번호" in txt:
            # 예: "조사번호: DT0001 · 안흥유원지"
            p.string = f"조사번호: {code} · {PARK_NAME}"

    # 3) 기본정보 카드 안의 조사번호(dd id="treeCodeText")도 확실히
    dd = soup.find("dd", id="treeCodeText")
    if dd:
        dd.string = code

    # 4) 빵부스러기(메인 · 안흥유원지 수목조사표) 문구/링크 교체
    #    a 태그 중 '안흥유원지' 포함된 텍스트를 찾아 바꿈
    for a in soup.find_all("a"):
        t = a.get_text(strip=True)
        if "안흥유원지" in t:
            a.string = f"{PARK_NAME} 수목조사표"
            # 공원 인덱스 링크(없어도 괜찮지만, 앞으로 만들 거라면 이게 정석)
            a["href"] = f"/parks/{PARK_NAME}/"

    # 5) 버튼/섹션 문구: "현장 기록 입력" / "수목 생육·관리 기록 입력" → "조사기록"
    #    (텍스트 기반으로 찾아서 교체: id 몰라도 됨)
    for h2 in soup.find_all(["h2", "h3"]):
        if "현장 기록 입력" in h2.get_text():
            h2.string = "조사기록"

    # 버튼은 a 또는 button일 수 있음 — 둘 다 검사
    for btn in soup.find_all(["a", "button"]):
        btxt = btn.get_text(" ", strip=True)
        if "수목 생육" in btxt or "관리 기록" in btxt or "기록 입력" in btxt:
            # 안흥유원지에서 원했던 느낌: '조사기록' 문구로
            btn.string = "조사기록 입력"

    # 6) 페이지 내에 남아있는 'DT0001', '안흥유원지'가 텍스트로 박혀있으면 정리
    #    (스크립트/스타일은 건드리지 않도록 text 노드만 치환)
    for node in soup.find_all(string=True):
        if node.parent.name in ["script", "style"]:
            continue
        s = str(node)
        s2 = s.replace("DT0001", code).replace("안흥유원지", PARK_NAME)
        if s2 != s:
            node.replace_with(s2)

    with open(path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    patched += 1

print(f"✅ 헤더/버튼 패치 완료: {patched}개")