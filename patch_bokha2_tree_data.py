import os
import pandas as pd
from bs4 import BeautifulSoup

XLSX = "Bokha2_trees.xlsx"
TREE_DIR = "trees"  # QR이 /trees/ 로 가므로 여기 파일을 수정

df = pd.read_excel(XLSX)
df.columns = [str(c).strip() for c in df.columns]

need_cols = ["수목코드","관리번호","성상","수종명","규격","단위","수량(설계)","수량(현장)"]
for c in need_cols:
    if c not in df.columns:
        raise ValueError(f"엑셀에 '{c}' 컬럼이 없습니다. 현재 컬럼: {list(df.columns)}")

# 숫자/빈칸 표시용
def v(x):
    if pd.isna(x): 
        return ""
    return str(x).strip()

# HTML에서 값을 찾아 넣는 헬퍼: <dd id="..."> 형태를 가정
def set_dd(soup, dd_id, value):
    tag = soup.find("dd", id=dd_id)
    if tag is not None:
        tag.string = value

ok = 0
for _, row in df.iterrows():
    code = v(row["수목코드"])
    url = v(row.get("QR_URL",""))
    if not code or code.lower() == "nan" or not url.startswith("http"):
        continue

    html_path = os.path.join(TREE_DIR, f"{code}.html")
    if not os.path.exists(html_path):
        continue

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # ✅ 조사번호(코드)
    set_dd(soup, "treeCodeText", code)

    # ✅ 기본정보 값 채우기 (템플릿의 id가 아래와 다르면 알려줘. 그럼 맞춰줄게)
    set_dd(soup, "manageNoText", v(row["관리번호"]))
    set_dd(soup, "typeText", v(row["성상"]))
    set_dd(soup, "speciesText", v(row["수종명"]))
    set_dd(soup, "specText", v(row["규격"]))
    set_dd(soup, "unitText", v(row["단위"]))
    set_dd(soup, "qtyDesignText", v(row["수량(설계)"]))
    set_dd(soup, "qtyFieldText", v(row["수량(현장)"]))

    # hidden input
    hidden = soup.find("input", id="treeCode")
    if hidden:
        hidden["value"] = code

    # QR 이미지 경로
    qr_img = soup.find("img", id="qrImage")
    if qr_img:
        qr_img["src"] = f"/qr/{code}.png"
        qr_img["alt"] = f"{code} QR 코드"

    # 페이지 URL 표시
    page_url_tag = soup.find("code", id="pageUrl")
    if page_url_tag:
        page_url_tag.string = f"https://theforim.com/trees/{code}.html"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    ok += 1

print(f"✅ 복하천 데이터 패치 완료: {ok}개")
