import os
import pandas as pd
from bs4 import BeautifulSoup

XLSX = "Bokha2_trees.xlsx"
TREE_DIR = "trees"

df = pd.read_excel(XLSX)
df.columns = [str(c).strip() for c in df.columns]

need = ["수목코드","QR_URL","관리번호","성상","수종명","규격","단위","수량(설계)","수량(현장)"]
for c in need:
    if c not in df.columns:
        raise ValueError(f"엑셀에 '{c}' 컬럼이 없습니다. 현재 컬럼: {list(df.columns)}")

def v(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

# "라벨 텍스트(dt)" -> 엑셀 컬럼명
LABEL_MAP = {
    "관리번호": "관리번호",
    "성상": "성상",
    "수종명": "수종명",
    "규격": "규격",
    "단위": "단위",
    "수량(설계)": "수량(설계)",
    "수량(현장)": "수량(현장)",
}

def set_value_by_label(soup, label_text, new_value):
    """
    <dt>관리번호</dt><dd>...</dd> 구조를 찾아 dd 값을 교체
    """
    # dt 중에서 텍스트가 label_text인 것을 찾는다
    for dt in soup.find_all("dt"):
        if dt.get_text(strip=True) == label_text:
            dd = dt.find_next_sibling("dd")
            if dd:
                dd.string = new_value
                return True
    return False

ok = 0
changed_any = 0

for _, row in df.iterrows():
    code = v(row["수목코드"])
    url  = v(row["QR_URL"])

    if not code or code.lower() == "nan":
        continue
    if not code.startswith("B2-"):
        continue
    if not url.startswith("http"):
        continue

    path = os.path.join(TREE_DIR, f"{code}.html")
    if not os.path.exists(path):
        continue

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 라벨 기반 교체
    local_changes = 0
    for label, col in LABEL_MAP.items():
        if set_value_by_label(soup, label, v(row[col])):
            local_changes += 1

    # 조사번호 표시도 확실히
    code_dd = soup.find("dd", id="treeCodeText")
    if code_dd:
        code_dd.string = code

    # URL 표시도 확실히
    page_url_tag = soup.find("code", id="pageUrl")
    if page_url_tag:
        page_url_tag.string = f"https://theforim.com/trees/{code}.html"

    # 저장
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    ok += 1
    if local_changes > 0:
        changed_any += 1

print(f"✅ 대상 파일 처리: {ok}개")
print(f"✅ 라벨 기반 값 교체 성공: {changed_any}개 (파일당 최소 1개 이상 값이 실제로 바뀐 수)")