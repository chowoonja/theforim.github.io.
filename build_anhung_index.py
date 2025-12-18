# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

PARK_DIR = ROOT / "parks" / "안흥유원지"
TREES_DIR = PARK_DIR / "trees"
OUT_INDEX = PARK_DIR / "index.html"

# DT0001 · 가죽나무 · 안흥유원지 · THE FORIM  (title에서 수종 추출)
TITLE_RE = re.compile(r"<title>\s*([A-Z]{2}\d{4})\s*·\s*(.*?)\s*·", re.IGNORECASE)

def extract_species(html_text: str, code: str) -> str:
    m = TITLE_RE.search(html_text)
    if m and m.group(1).upper() == code.upper():
        return m.group(2).strip()
    # fallback: h1/h2에서라도 추출 시도
    m2 = re.search(rf">{re.escape(code)}\s*·\s*([^<]+)<", html_text)
    if m2:
        return m2.group(1).strip()
    return ""

def read_utf8(path: Path) -> str:
    # 대부분 UTF-8이지만, 혹시 BOM이 섞여도 안전하게 읽기
    return path.read_text(encoding="utf-8-sig", errors="replace")

def backup_existing_index():
    if OUT_INDEX.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = OUT_INDEX.with_name(f"index_backup_{stamp}.html")
        backup.write_text(OUT_INDEX.read_text(encoding="utf-8-sig", errors="replace"), encoding="utf-8")
        print(f"[백업 생성] {backup}")

def build_rows(tree_files: list[Path]) -> str:
    rows = []
    for f in tree_files:
        code = f.stem  # DT0001
        html_text = read_utf8(f)
        species = extract_species(html_text, code)

        # 링크: park index 기준으로 ./trees/DT0001.html
        detail_href = f"./trees/{code}.html"
        qr_href = f"/qr/{code}.png"  # qr 폴더가 루트에 있으니 /qr/...

        rows.append(f"""
          <tr>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec;">
              <a href="{detail_href}" style="color: #2f6c4f; font-weight: 600;">{code}</a>
            </td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec;">{species}</td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec; text-align: right;"></td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec; text-align: right;"></td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec; text-align: right;"></td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec;"></td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec;"></td>
            <td style="padding: 0.45rem; border-bottom: 1px solid #ecf0ec; text-align: center;">
              <a href="{qr_href}" target="_blank">QR보기</a>
            </td>
          </tr>
        """.rstrip())
    return "\n".join(rows)

def main():
    if not TREES_DIR.exists():
        raise SystemExit(f"[오류] trees 폴더가 없습니다: {TREES_DIR}")

    tree_files = sorted(
        TREES_DIR.glob("??[0-9][0-9][0-9][0-9].html"),
        key=lambda p: (p.stem[:2], int(p.stem[2:]))  # DT 먼저, ET 다음(원하면 바꿀 수 있음)
    )
    if not tree_files:
        raise SystemExit("[오류] DT/ET html 파일을 찾지 못했습니다. (예: DT0001.html)")

    backup_existing_index()

    rows_html = build_rows(tree_files)

    out_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>안흥유원지 수목조사표 · THE FORIM</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="/assets/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="logo-mark">THE FORIM</div>
    <div class="brand-text">
      <h1>안흥유원지 수목조사표</h1>
      <p>공간별 · 개체별 수목 현황과 QR 연동 정보를 관리합니다.</p>
    </div>
  </header>

  <main class="container">
    <nav style="margin: 1rem 0 1.5rem; font-size: 0.9rem;">
      <a href="/">← 메인으로 돌아가기</a>
    </nav>

    <section class="card">
      <h2 style="margin-top: 0;">기본 정보</h2>
      <p style="margin-bottom: 0.8rem; font-size: 0.95rem;">
        공원명: <strong>안흥유원지</strong><br />
        조사일: <span>YYYY-MM-DD</span><br />
        조사자: <span>더포림</span>
      </p>
    </section>

    <section class="card" style="margin-top: 1.5rem; overflow-x: auto;">
      <h2 style="margin-top: 0;">수목 목록</h2>
      <p style="font-size: 0.9rem; color: #555;">
        ※ 조사번호(DT/ET)를 클릭하면 개별 수목 상세 페이지로 이동합니다.<br />
        ※ DT = 낙엽교목, ET = 상록교목 분류 코드입니다.
      </p>

      <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
        <thead>
          <tr style="background: #f0f5f1;">
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">조사번호</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">수종</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">수고(m)</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">흉고직경(cm)</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">수관폭(m)</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">생육상태</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">세부 위치</th>
            <th style="padding: 0.5rem; border-bottom: 1px solid #dde6dd;">QR</th>
          </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
      </table>

      <p style="margin-top: 0.8rem; font-size: 0.85rem; color: #666;">
        ※ 목록은 필요에 따라 계속 추가/수정할 수 있습니다.
      </p>
    </section>
  </main>

  <footer class="site-footer">
    <small>© THE FORIM · 안흥유원지 수목조사</small>
  </footer>
</body>
</html>
"""
    OUT_INDEX.write_text(out_html, encoding="utf-8")
    print(f"[완료] 생성: {OUT_INDEX}")
    print(f"[총 {len(tree_files)}개] DT/ET 상세페이지 링크를 index에 반영했습니다.")

if __name__ == "__main__":
    main()