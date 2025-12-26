import os
import re
from urllib.parse import quote

PARK_NAME = "복하천 제2수변공원"

FORM_BASE = "https://docs.google.com/forms/d/e/1FAIpQLSdgujOIV9bKAUyOAot7AoysT4UWBrrIKkQbIgWirDtZjaapQA/viewform"
ENTRY_PARK = "939121262"
ENTRY_CODE = "253022448"

TREES_DIR = os.path.join("parks", "bokha2", "trees")

CODE_RE = re.compile(r"\b(B2-[A-Z0-9]{5,})\b", re.IGNORECASE)

def build_url(code: str):
    return (
        f"{FORM_BASE}?usp=pp_url"
        f"&entry.{ENTRY_PARK}={quote(PARK_NAME, safe='')}"
        f"&entry.{ENTRY_CODE}={quote(code, safe='')}"
    )

def main():
    changed = 0
    total = 0

    for fn in os.listdir(TREES_DIR):
        if not fn.lower().endswith(".html"):
            continue
        total += 1

        m = CODE_RE.search(fn.upper())
        if not m:
            continue
        code = m.group(1).upper()
        url = build_url(code)

        path = os.path.join(TREES_DIR, fn)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        # 1) 공원명 input에 value 기본값 넣기 (placeholder는 유지)
        html2 = re.sub(
            r'(<input[^>]*id="parkName"[^>]*)(>)',
            lambda mm: (mm.group(1) + f' value="{PARK_NAME}"' if 'value=' not in mm.group(1) else mm.group(0)) + mm.group(2),
            html,
            flags=re.IGNORECASE
        )

        # 2) 조사기록 버튼 href를 고정 prefill로 세팅
        html2 = re.sub(
            r'(<a\b[^>]*\bid\s*=\s*"openFormBtn"[^>]*\bhref\s*=\s*")[^"]*(")',
            r'\1' + url + r'\2',
            html2,
            flags=re.IGNORECASE
        )

        # 3) JS에서 parkName을 비워두는 경우가 있으니, loadHeaderInfo 후 parkName이 비면 PARK_NAME 넣게 보강
        if "if (!document.getElementById(\"parkName\").value)" not in html2:
            html2 = html2.replace(
                "loadHeaderInfo();",
                "loadHeaderInfo();\n      if (!document.getElementById(\"parkName\").value) { document.getElementById(\"parkName\").value = \"" + PARK_NAME + "\"; }"
            )

        if html2 != html:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(html2)
            changed += 1

    print(f"✅ 완료: 공원명 자동입력 + 조사기록 링크 고정 | 변경 {changed} | 총 {total}")

if __name__ == "__main__":
    main()