from pathlib import Path
p = Path(r".\parks\안흥유원지\trees\DT0001.html")
txt = p.read_text(encoding="utf-8", errors="replace")
changed = False
tail = "\n"
# <main> 열려있는데 닫힘이 없으면 닫아주기
if "<main" in txt.lower() and "</main" not in txt.lower():
    tail = "\n</main>\n"
    changed = True
# </body> 없으면 추가
if "</body" not in txt.lower():
    tail += "</body>\n"
    changed = True
# </html> 없으면 추가
if "</html" not in txt.lower():
    tail += "</html>\n"
    changed = True
if changed:
    p.write_text(txt.rstrip() + tail, encoding="utf-8")
    print("OK: DT0001.html 보정 완료 (닫힘 태그 추가)")
else:
    print("OK: DT0001.html 이미 정상(변경 없음)")
