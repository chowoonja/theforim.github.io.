from pathlib import Path
import re

p = Path(r"./parks/안흥유원지/trees/DT0001.html")
txt = p.read_text(encoding="utf-8", errors="replace")

# 1) <title> 교체
txt = re.sub(
    r"<title>.*?</title>",
    "<title>DT0001 · 가죽나무 · 안흥유원지 · THE FORIM</title>",
    txt,
    flags=re.I | re.S
)

# 2) 헤더(h1/p) 교체
txt = re.sub(
    r"<h1>.*?</h1>",
    "<h1>수목 상세 정보</h1>",
    txt,
    flags=re.I | re.S
)
txt = re.sub(
    r"<p>.*?</p>",
    "<p>조사번호: DT0001 · 안흥유원지</p>",
    txt,
    count=1,
    flags=re.I | re.S
)

# 3) 내비게이션 텍스트 교체(링크는 유지)
txt = re.sub(r'>\s*[^<]*\s*</a>\s*쨌', r'>메인</a> ·', txt, count=1, flags=re.S)
txt = re.sub(r'href="/parks/[^"]*/"\s*>\s*[^<]*\s*<', 'href="/parks/안흥유원지/">안흥유원지 수목조사표<', txt, count=1, flags=re.S)

p.write_text(txt, encoding="utf-8", newline="\n")
print("OK: DT0001 템플릿(타이틀/헤더/내비) 한글 교정 완료")