from pathlib import Path
import re

ROOT = Path(".").resolve()
TREES = ROOT / "parks" / "안흥유원지" / "trees"

def get_code_from_filename(p: Path) -> str:
    # DT0001.html / ET0090.html 같은 파일명에서 코드만 추출
    m = re.match(r"^(DT|ET)\d{4}$", p.stem, flags=re.I)
    return p.stem.upper() if m else p.stem

def fix_one(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8", errors="replace")

    code = get_code_from_filename(path)

    changed = False

    # 1) 헤더 h1 고정 (첫번째 <h1>만)
    new_txt = re.sub(r"<h1>.*?</h1>", "<h1>수목 상세 정보</h1>", txt, count=1, flags=re.I | re.S)
    if new_txt != txt:
        txt = new_txt
        changed = True

    # 2) 헤더 p 고정 (첫번째 <p>만 / 조사번호 문구로)
    new_p = f"<p>조사번호: {code} · 안흥유원지</p>"
    new_txt = re.sub(r"<p>.*?</p>", new_p, txt, count=1, flags=re.I | re.S)
    if new_txt != txt:
        txt = new_txt
        changed = True

    # 3) 내비 첫 링크 텍스트를 "메인"으로 (href는 유지)
    #    <a href="/"> ... </a> 부분의 텍스트만 교체
    new_txt = re.sub(r'(<a\s+href="/"\s*>)[^<]*(</a>)', r"\1메인\2", txt, count=1, flags=re.I | re.S)
    if new_txt != txt:
        txt = new_txt
        changed = True

    # 4) 구분자(쨌 등) -> " · "로 정리 (메인 링크 뒤 구간만 1회)
    new_txt = re.sub(r'(</a>)\s*[^<]{0,5}\s*', r"\1 · ", txt, count=1, flags=re.S)
    if new_txt != txt:
        txt = new_txt
        changed = True

    # 5) 두번째 링크를 /parks/안흥유원지/ 로 고정 + 텍스트를 "안흥유원지 수목조사표"
    #    링크 href가 깨져있어도 통째로 고정해버림(첫 1회만)
    new_txt = re.sub(
        r'<a\s+href="/parks/[^"]*/"\s*>.*?</a>',
        '<a href="/parks/안흥유원지/">안흥유원지 수목조사표</a>',
        txt,
        count=1,
        flags=re.I | re.S
    )
    if new_txt != txt:
        txt = new_txt
        changed = True

    if changed:
        path.write_text(txt, encoding="utf-8", newline="\n")
    return changed

def main():
    if not TREES.exists():
        print(f"[에러] trees 폴더를 찾지 못했습니다: {TREES}")
        return

    total = 0
    changed = 0
    skipped = 0

    for p in sorted(TREES.glob("*.html")):
        total += 1
        try:
            if fix_one(p):
                changed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"[에러] {p.name}: {e}")

    print(f"OK: 헤더/내비 한글 교정 완료 | 변경 {changed} | 스킵 {skipped} | 총 {total}")

if __name__ == "__main__":
    main()