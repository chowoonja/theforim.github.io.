from pathlib import Path
import re

ROOT = Path(".").resolve()
TREES = ROOT / "parks" / "안흥유원지" / "trees"

pattern = re.compile(r"<title\b[^>]*>.*?</title>", re.IGNORECASE | re.DOTALL)

changed = 0
total = 0

for p in TREES.glob("*.html"):
    total += 1
    code = p.stem  # DT0001, ET0090 ...
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        # 혹시 인코딩이 엉켜있으면 일단 바이트로 읽어서 UTF-8로 최대한 복구
        raw = p.read_bytes()
        txt = raw.decode("utf-8", errors="replace")

    new_title = f"<title>{code} · 안흥유원지 · THE FORIM</title>"

    if pattern.search(txt):
        txt2 = pattern.sub(new_title, txt, count=1)
    else:
        # title 태그가 아예 없으면 head 안에 넣기
        txt2 = re.sub(r"(<head\b[^>]*>)", r"\1\n" + new_title, txt, count=1, flags=re.I)

    if txt2 != txt:
        p.write_text(txt2, encoding="utf-8", newline="\n")
        changed += 1

print(f"OK: title 강제 교체 완료 | 변경 {changed} | 총 {total}")