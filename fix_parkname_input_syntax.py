import os, re

TREES_DIR = os.path.join("parks", "bokha2", "trees")
PARK_NAME = "복하천 제2수변공원"

def fix_one(html: str) -> str:
    # 1) 잘못된 형태: type="text"/ value="..."
    html = re.sub(
        r'(id="parkName"[^>]*type="text")\s*/\s*(value="[^"]*")',
        r'\1 \2',
        html,
        flags=re.IGNORECASE
    )

    # 2) parkName input에 value가 없으면 value 추가 (정상 input 태그에만)
    def add_value(m):
        tag = m.group(0)
        if re.search(r'\bvalue\s*=\s*"', tag, flags=re.IGNORECASE):
            return tag
        # 끝의 > 또는 /> 앞에 value 삽입
        return re.sub(r'\s*/?>$', f' value="{PARK_NAME}"/>', tag)

    html = re.sub(
        r'<input\b[^>]*\bid\s*=\s*"parkName"[^>]*>',
        add_value,
        html,
        flags=re.IGNORECASE
    )

    # 3) 혹시 JS가 loadHeaderInfo()로 빈칸 덮어쓰면, 비어있을 때 기본값 다시 넣기
    if 'loadHeaderInfo();' in html and 'parkNameDefaultInjected' not in html:
        html = html.replace(
            'loadHeaderInfo();',
            'loadHeaderInfo();\n      // parkNameDefaultInjected\n      if (!document.getElementById("parkName").value) { document.getElementById("parkName").value = "' + PARK_NAME + '"; }'
        )

    return html

def main():
    changed = 0
    total = 0
    for fn in os.listdir(TREES_DIR):
        if not fn.lower().endswith(".html"):
            continue
        total += 1
        path = os.path.join(TREES_DIR, fn)
        with open(path, "r", encoding="utf-8") as f:
            old = f.read()
        new = fix_one(old)
        if new != old:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
            changed += 1
    print(f"✅ parkName input 문법/기본값 수정: 변경 {changed} / 총 {total}")

if __name__ == "__main__":
    main()