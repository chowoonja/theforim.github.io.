import os
import re
from urllib.parse import quote

# === 설정 ===
FORM_BASE = "https://docs.google.com/forms/d/e/1FAIpQLSdgujOIV9bKAUyOAot7AoysT4UWBrrIKkQbIgWirDtZjaapQA/viewform"
ENTRY_PARK = "939121262"   # 공원명 entry
ENTRY_CODE = "253024248"   # 수목코드 entry
PARK_NAME = "안흥유원지"

TREES_DIR = os.path.join("parks", "안흥유원지", "trees")

# 수목코드 추출: DT0001, ET0106, DS..., ES... 등(영문 2자 + 숫자)
CODE_RE = re.compile(r"\b([A-Z]{2}\d{4})\b", re.IGNORECASE)

def build_prefill_url(tree_code: str) -> str:
    # URL 인코딩
    park_q = quote(PARK_NAME, safe="")
    code_q = quote(tree_code, safe="")
    return f"{FORM_BASE}?usp=pp_url&entry.{ENTRY_PARK}={park_q}&entry.{ENTRY_CODE}={code_q}"

def main():
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

        # 파일명에서 코드 추출(가장 안전)
        m = CODE_RE.search(fn.upper())
        if not m:
            skipped += 1
            continue
        tree_code = m.group(1).upper()

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        # openFormBtn 앵커를 찾아 href를 바꿈
        # - id="openFormBtn"가 있는 <a ...> 태그의 href만 교체
        new_url = build_prefill_url(tree_code)

        def repl(match):
            # match: <a ... id="openFormBtn" ... href="..." ...>
            tag = match.group(0)
            # href="..."만 교체
            tag2 = re.sub(r'href\s*=\s*"[^"]*"', f'href="{new_url}"', tag, flags=re.IGNORECASE)
            return tag2

        new_html, n = re.subn(
            r'<a\b[^>]*\bid\s*=\s*"openFormBtn"[^>]*>',
            repl,
            html,
            flags=re.IGNORECASE
        )

        if n == 0:
            # id가 없으면 스킵 (안전)
            skipped += 1
            continue

        if new_html != html:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_html)
            changed += 1
        else:
            skipped += 1

    print(f"OK: 조사기록 prefill 링크 적용 | 변경 {changed} | 스킵 {skipped} | 총 {total}")
    print(f"대상 폴더: {TREES_DIR}")

if __name__ == "__main__":
    main()