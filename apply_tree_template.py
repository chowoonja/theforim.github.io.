import os
from bs4 import BeautifulSoup

# 템플릿 파일 위치 (DT0001 모양의 기본 틀)
TEMPLATE_PATH = "parks/안흥유원지/tree_template.html"

# 실제 나무 HTML 파일들이 들어 있는 폴더
TARGET_DIR =  "parks/안흥유원지/trees"

# 대상 파일 목록 (DT****.html, ET****.html 모두)
tree_files = [
    f for f in os.listdir(TARGET_DIR)
    if (f.startswith("DT") or f.startswith("ET")) and f.endswith(".html")
]

# 템플릿 HTML 한 번만 읽기
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template_html = f.read()

for filename in tree_files:
    tree_code = os.path.splitext(filename)[0]  # 예: DT0001

    # 매번 새로 soup 만들기
    soup = BeautifulSoup(template_html, "html.parser")

    # ① 조사번호(코드) 표시 부분 <dd id="treeCodeText"> 바꾸기
    code_tag = soup.find("dd", id="treeCodeText")
    if code_tag:
        code_tag.string = tree_code

    # ② hidden input 값 바꾸기 <input id="treeCode">
    hidden = soup.find("input", id="treeCode")
    if hidden:
        hidden["value"] = tree_code

    # ③ QR 이미지 경로 바꾸기 <img id="qrImage">
    qr_img = soup.find("img", id="qrImage")
    if qr_img:
        qr_img["src"] = f"/qr/{tree_code}.png"
        qr_img["alt"] = f"{tree_code} QR 코드"

    # ④ 페이지 URL 표시 텍스트 바꾸기 <code id="pageUrl">
    page_url_tag = soup.find("code", id="pageUrl")
    if page_url_tag:
        page_url_tag.string = f"https://theforim.com/parks/안흥유원지/trees/{tree_code}.html"

    # ⑤ 결과를 parks/안흥유원지/trees/ 아래에 저장
    out_path = os.path.join(TARGET_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"{filename} 생성 완료")

