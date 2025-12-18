import os
import re
from bs4 import BeautifulSoup

# ✅ 1) DT0001(정답 템플릿) 파일 위치
# 보통 parks/안흥유원지/trees 안에 있음. 혹시 아니면 trees 쪽도 자동으로 탐색함.
CANDIDATE_DIRS = [
    os.path.join("parks", "안흥유원지", "trees"),
    "trees",
]

def find_target_dir():
    for d in CANDIDATE_DIRS:
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "DT0001.html")):
            return d
    return None

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def extract_basic_info(html):
    """
    기존 파일에서 '기본 정보' dl(조사번호/관리번호/성상/수종명/규격...)을 최대한 추출
    """
    soup = BeautifulSoup(html, "html.parser")
    # '기본 정보' 섹션 찾기
    h2 = None
    for tag in soup.find_all(["h2"]):
        if tag.get_text(strip=True) == "기본 정보":
            h2 = tag
            break

    if not h2:
        return None

    section = h2.find_parent("section")
    if not section:
        return None

    dl = section.find("dl")
    if not dl:
        return None

    # dt/dd 쌍 추출
    items = []
    dts = dl.find_all("dt")
    for dt in dts:
        dd = dt.find_next_sibling("dd")
        if dd:
            items.append((dt.get_text(strip=True), dd.get_text(strip=True)))
    return items

def extract_title_parts(html):
    """
    <title>DT0004 · 느티나무 · 안흥유원지 · THE FORIM</title>
    여기서 DT코드/수종명/공원명을 뽑음 (최소한 DT코드는 필수)
    """
    soup = BeautifulSoup(html, "html.parser")
    t = soup.title.get_text(strip=True) if soup.title else ""
    # 대충 "DT0004 · 느티나무 · 안흥유원지 · THE FORIM"
    parts = [p.strip() for p in t.split("·")]
    dtcode = None
    species = None
    park = None
    if parts:
        m = re.search(r"(DT\d{4})", parts[0])
        if m:
            dtcode = m.group(1)
    if len(parts) >= 2:
        species = parts[1]
    if len(parts) >= 3:
        park = parts[2]
    return dtcode, species, park

def build_dl_html(items):
    """
    dt/dd 목록을 DT0001 스타일 DL로 생성
    """
    if not items:
        return ""
    rows = []
    for dt, dd in items:
        rows.append(f"<dt>{dt}</dt><dd>{dd}</dd>")
    inner = "\n        ".join(rows)
    return f"""
      <dl style="display: grid; grid-template-columns: 120px 1fr; row-gap: 0.35rem; margin: 0;">
        {inner}
      </dl>
""".rstrip()

def make_page(dtcode, species, park, basic_items, template_soup):
    """
    DT0001 템플릿을 기반으로,
    - title / 조사번호 표시 / treeCode / QR이미지 / 페이지URL
    - 기본정보 DL만 대상 파일 값으로 교체
    """
    soup = BeautifulSoup(str(template_soup), "html.parser")

    # (1) title
    if soup.title and dtcode:
        # 템플릿 title의 "DT0001"과 "가죽나무"를 교체
        new_title = soup.title.get_text()
        new_title = re.sub(r"DT\d{4}", dtcode, new_title)
        if species:
            # 가운데 수종명만 대체 (안전하게 '·' 기준 2번째를 바꾸는 방식 대신 간단 대체)
            # 템플릿이 "DT0001 · 가죽나무 · 안흥유원지 · THE FORIM" 형태라 가정
            new_title = re.sub(r"·\s*[^·]+?\s*·", f"· {species} ·", new_title, count=1)
        if park:
            new_title = re.sub(r"·\s*[^·]+?\s*·\s*THE FORIM", f"· {park} · THE FORIM", new_title, count=1)
        soup.title.string = new_title.strip()

    # (2) 상단 헤더의 조사번호 문구 교체
    p = soup.find("p", string=re.compile(r"조사번호:"))
    if p and dtcode:
        txt = p.get_text()
        txt = re.sub(r"DT\d{4}", dtcode, txt)
        if park:
            txt = re.sub(r"·\s*.+$", f"· {park}", txt)  # 끝쪽 공원명 갱신
        p.string = txt

    # (3) hidden treeCode 값 교체
    treecode_input = soup.find("input", {"id": "treeCode"})
    if treecode_input and dtcode:
        treecode_input["value"] = dtcode

    # (4) 기본정보 DL 교체
    # 템플릿에서 '기본 정보' 섹션 찾아 dl 통째로 교체
    h2 = None
    for tag in soup.find_all("h2"):
        if tag.get_text(strip=True) == "기본 정보":
            h2 = tag
            break
    if h2:
        section = h2.find_parent("section")
        if section:
            old_dl = section.find("dl")
            if old_dl:
                old_dl.replace_with(BeautifulSoup(build_dl_html(basic_items), "html.parser"))

    # (5) QR 이미지 파일/페이지URL 표기 교체
    # img src="/qr/DT0001.png" 를 DT코드로 변경
    qr_img = soup.find("img", {"alt": re.compile(r"QR 코드")})
    if qr_img and dtcode:
        qr_img["src"] = f"/qr/{dtcode}.png"
        qr_img["alt"] = f"{dtcode} QR 코드"

    # 페이지 URL 문구도 DT코드 + (공원 경로)로 맞춤
    # 템플릿에 "https://theforim.com/trees/DT0001.html" 같은게 있으면 교체
    page_url_code = soup.find(string=re.compile(r"https://theforim\.com/"))
    # 여러 군데 있을 수 있어서 전체 교체
    for node in soup.find_all(string=re.compile(r"https://theforim\.com/")):
        # 실제 정답 경로에 맞춤
        # parks/안흥유원지/trees/DT0001.html 형태로
        if dtcode:
            new = re.sub(r"https://theforim\.com/.*?(DT\d{4}\.html)", f"https://theforim.com/parks/안흥유원지/trees/{dtcode}.html", node)
            node.replace_with(new)

    # (6) head/body 구조가 깨진 파일 방지: soup 자체가 정상 HTML로 출력
    out = str(soup)

    # 가끔 BeautifulSoup가 <html><head>... 넣는 경우가 있는데, 템플릿 자체를 유지하는 게 중요하니
    # 템플릿이 이미 정상이면 그대로 잘 나옴.
    return out

def main():
    target_dir = find_target_dir()
    if not target_dir:
        print("❌ DT0001.html이 있는 폴더를 찾지 못했습니다.")
        print("   parks/안흥유원지/trees 또는 trees 안에 DT0001.html이 있는지 확인해 주세요.")
        return

    template_path = os.path.join(target_dir, "DT0001.html")
    template_html = read_file(template_path)
    template_soup = BeautifulSoup(template_html, "html.parser")

    # DT 대상 파일들 (DT0001 제외)
    files = sorted([f for f in os.listdir(target_dir) if re.match(r"^DT\d{4}\.html$", f)])
    if not files:
        print("❌ DT 파일을 찾지 못했습니다:", target_dir)
        return

    updated = 0
    skipped = 0

    for fname in files:
        if fname == "DT0001.html":
            continue

        path = os.path.join(target_dir, fname)
        html = read_file(path)

        dtcode, species, park = extract_title_parts(html)
        basic_items = extract_basic_info(html)

        # 최소 안전장치
        if not dtcode:
            print("⚠️  건너뜀(코드 추출 실패):", fname)
            skipped += 1
            continue
        if not basic_items:
            # 기본정보가 없으면 파일 구조가 너무 깨졌다는 뜻이므로 그래도 DT코드 기반으로 생성은 가능
            basic_items = [("조사번호", dtcode)]

        new_html = make_page(dtcode, species, park, basic_items, template_soup)
        write_file(path, new_html)
        updated += 1

    print("=== DT 페이지를 DT0001 템플릿으로 통일 완료 ===")
    print("대상 폴더:", target_dir)
    print("수정됨:", updated)
    print("건너뜀:", skipped)

if __name__ == "__main__":
    main()