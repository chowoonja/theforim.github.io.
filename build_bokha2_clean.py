import os
import pandas as pd
from bs4 import BeautifulSoup

# ===== 설정 =====
XLSX = "Bokha2_trees.xlsx"
TEMPLATE_PATH = "parks/안흥유원지/tree_template.html"
OUT_DIR = "trees"
os.makedirs(OUT_DIR, exist_ok=True)

# ===== 엑셀 읽기 =====
df = pd.read_excel(XLSX)
df.columns = [str(c).strip() for c in df.columns]

required = ["수목코드", "QR_URL"]
for c in required:
    if c not in df.columns:
        raise ValueError(f"엑셀에 '{c}' 컬럼이 없습니다.")

# ===== 템플릿 =====
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template_html = f.read()

def v(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

created = 0

for _, row in df.iterrows():
    code = v(row["수목코드"])
    url  = v(row["QR_URL"])

    # ✅ 복하천 유효 코드만
    if not code or code.lower() == "nan":
        continue
    if not code.startswith("B2-"):
        continue
    if not url.startswith("http"):
        continue

    soup = BeautifulSoup(template_html, "html.parser")

    # 조사번호
    code_tag = soup.find("dd", id="treeCodeText")
    if code_tag:
        code_tag.string = code

    hidden = soup.find("input", id="treeCode")
    if hidden:
        hidden["value"] = code

    # QR
    qr_img = soup.find("img", id="qrImage")
    if qr_img:
        qr_img["src"] = f"/qr/{code}.png"
        qr_img["alt"] = f"{code} QR 코드"

    # URL
    page_url = soup.find("code", id="pageUrl")
    if page_url:
        page_url.string = f"https://theforim.com/trees/{code}.html"

    # 저장
    out_path = os.path.join(OUT_DIR, f"{code}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    created += 1

print(f"✅ 복하천 HTML 새로 생성 완료: {created}개")