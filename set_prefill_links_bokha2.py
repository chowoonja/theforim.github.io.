import os
import re
from urllib.parse import quote

# === 설정(복하천용) ===
FORM_BASE = "https://docs.google.com/forms/d/e/1FAIpQLSdgujOIV9bKAUyOAot7AoysT4UWBrrIKkQbIgWirDtZjaapQA/viewform"

# ✅ 여기 entry 번호는 '폼' 기준으로 고정
ENTRY_PARK = "939121262"    # 공원명 entry
ENTRY_CODE = "253022448"    # 수목코드 entry  (네 Network 캡처 기준)

# ✅ 공원명(표시용)
PARK_NAME = "복하천 제2수변공원"

# ✅ 대상 trees 폴더
TREES_DIR = os.path.join("parks", "복하천제2수변공원", "trees")

# 파일명에서 수목코드 추출(복하천 코드: B2-XXXXXXX 형태)
CODE_RE = re.compile(r"\b(B2-[A-Z0-9]{5,})\b", re.IGNORECASE)

def build_prefill_url(tree_code: str) -> str:
    park_q = quote(PARK_NAME, safe="")
    code_q = quote(tree_code, safe="")
    return f"{FORM_BASE}?usp=pp_url&entry.{ENTRY_PARK}={park_q}&entry.{ENTRY_CODE}={code_q}"

def main():
    print("✅ set_prefill_links_bokha2.py 실행 시작")
    if not os.path.isdir(TREES_DIR):
        raise SystemExit(f"[ERROR] TREES 폴더를 찾을 수 없습니다: {TREES_DIR}")

    changed = 0
    skipped = 0
    total = 0

    for fn in os.listdir(TREES_DIR):
        if not fn.lower().endswith(".html"):
            continue
        total += 1

        path = os.path.join(TREES_DIR, fn)

        m = CODE_RE.search(fn.upper())
        if not m:
            skipped += 1
            continue
        tree_code = m.group(1).upper()

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        new_url = build_prefill_url(tree_code)

        def repl(match):
            tag = match.group(0)
            tag2 = re.sub(r'href\s*=\s*"[^"]*"', f'href="{new_url}"', tag, flags=re.IGNORECASE)
            return tag2

        new_html, n = re.subn(
            r'<a\b[^>]*\bid\s*=\s*"openFormBtn"[^>]*>',
            repl,
            html,
            flags=re.IGNORECASE
        )

        if n == 0:
            skipped += 1
            continue

        if new_html != html:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_html)
            changed += 1
        else:
            skipped += 1

    print(f"OK: 복하천 조사기록 prefill 링크 적용 | 변경 {changed} | 스킵 {skipped} | 총 {total}")
    print(f"대상 폴더: {TREES_DIR}")

if __name__ == "__main__":
    main()