from pathlib import Path
import re

ROOT = Path(r".\parks\안흥유원지\trees")
FILES = sorted(ROOT.glob("*.html"))

title_re = re.compile(r"<title>.*?</title>", re.I | re.S)

changed = 0
skipped = 0

for p in FILES:
    code = p.stem  # DT0001 / ET0090 ...
    txt = p.read_text(encoding="utf-8", errors="replace")

    new_title = f"<title>{code} · 안흥유원지 · THE FORIM</title>"

    if title_re.search(txt):
        txt2 = title_re.sub(new_title, txt, count=1)
    else:
        # title이 없으면 head 바로 다음에 삽입
        txt2 = re.sub(r"(<head\b[^>]*>\s*)", r"\1" + new_title + "\n", txt, flags=re.I)

    if txt2 != txt:
        p.write_text(txt2, encoding="utf-8", newline="\n")
        changed += 1
    else:
        skipped += 1

print(f"OK: title 교체 완료 | 변경 {changed} | 스킵 {skipped} | 총 {len(FILES)}")