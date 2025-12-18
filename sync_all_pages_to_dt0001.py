from pathlib import Path
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PARK_TREES_DIR = ROOT / "parks" / "안흥유원지" / "trees"
TEMPLATE_FILE = PARK_TREES_DIR / "DT0001.html"
TARGET_GLOBS = ["DT*.html", "ET*.html"]

def make_backup(file_path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = file_path.with_name(f"{file_path.stem}_backup_{ts}{file_path.suffix}")
    backup.write_text(file_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    return backup

def read_text(fp: Path) -> str:
    # 깨진 문자가 있어도 멈추지 않게 errors="replace"
    return fp.read_text(encoding="utf-8", errors="replace")

def split_head_body_strict(html: str):
    m_head = re.search(r"<head\b[^>]*>.*?</head\s*>", html, re.IGNORECASE | re.DOTALL)
    m_body = re.search(r"<body\b[^>]*>(.*)</body\s*>", html, re.IGNORECASE | re.DOTALL)
    if not m_head or not m_body:
        return None
    return m_head.group(0), m_body.group(1)

def extract_template_head(template_html: str) -> str:
    parts = split_head_body_strict(template_html)
    if not parts:
        raise ValueError("DT0001.html(템플릿)에서 head/body를 찾지 못했습니다. DT0001이 정상 HTML인지 확인 필요.")
    tpl_head, _ = parts
    return tpl_head

def get_doctype_and_html_open(template_html: str):
    doctype = "<!DOCTYPE html>"
    m_doctype = re.search(r"<!DOCTYPE[^>]*>", template_html, re.IGNORECASE)
    if m_doctype:
        doctype = m_doctype.group(0)

    html_open = '<html lang="ko">'
    m_html_open = re.search(r"<html\b[^>]*>", template_html, re.IGNORECASE)
    if m_html_open:
        html_open = m_html_open.group(0)

    return doctype, html_open

def normalize_body_inner(raw: str) -> str:
    """
    파일이 조각이거나 깨져 있어도 body 안쪽으로 넣을 수 있게 최소 정리.
    - BOM/널문자 제거
    """
    raw = raw.replace("\ufeff", "")
    raw = raw.replace("\x00", "")
    return raw.strip()

def rebuild(template_html: str, target_html: str):
    tpl_head = extract_template_head(template_html)
    doctype, html_open = get_doctype_and_html_open(template_html)

    strict = split_head_body_strict(target_html)
    if strict:
        # 정상 HTML: body 안쪽만 유지
        _, tgt_body_inner = strict
        body_inner = tgt_body_inner
    else:
        # 비정상 HTML(조각): 파일 전체를 body 내용으로 간주
        body_inner = target_html

    body_inner = normalize_body_inner(body_inner)

    new_html = (
        f"{doctype}\n"
        f"{html_open}\n"
        f"{tpl_head}\n"
        f"<body>\n{body_inner}\n</body>\n"
        f"</html>\n"
    )
    return new_html

def main():
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"템플릿 파일이 없습니다: {TEMPLATE_FILE}")

    template_html = read_text(TEMPLATE_FILE)

    files = []
    for g in TARGET_GLOBS:
        files.extend(PARK_TREES_DIR.glob(g))
    files = sorted(set(files))

    if not files:
        print("[중단] 대상 파일을 찾지 못했습니다.")
        return

    changed = 0
    skipped = 0
    errors = 0

    for fp in files:
        if fp.name == TEMPLATE_FILE.name:
            skipped += 1
            continue

        try:
            old = read_text(fp)
            new_html = rebuild(template_html, old)

            if new_html == old:
                skipped += 1
                continue

            make_backup(fp)
            fp.write_text(new_html, encoding="utf-8")
            changed += 1

        except Exception as e:
            print(f"[에러] {fp.name}: {e}")
            errors += 1

    print("=== DT/ET 전체 복구 + 템플릿(head) 적용 완료 ===")
    print(f"대상 폴더: {PARK_TREES_DIR}")
    print(f"수정됨: {changed}")
    print(f"건너뜀: {skipped}")
    print(f"에러: {errors}")
    print(f"총 파일: {len(files)}")

if __name__ == "__main__":
    main()