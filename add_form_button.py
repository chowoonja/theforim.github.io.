# coding: utf-8
import os
from bs4 import BeautifulSoup

# 현재 파일 기준으로 루트 찾기
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 안흥유원지 트리 HTML들이 있는 폴더
TARGET_DIR = os.path.join(BASE_DIR, "parks", "안흥유원지", "trees")

# DT0001에 있는 "설명 + 버튼" 블록
BUTTON_SNIPPET = """
<p>
  현장에서 생육 상태와 필요 관리 내용을 기록하려면 아래 버튼을 눌러 주세요.
</p>

<!-- 기존 고정 링크 대신, JS로 폼 URL을 생성하도록 버튼에 id 부여 -->
<a href="#" id="openFormBtn" style="
    display: inline-block;
    padding: 0.7rem 1.4rem;
    border-radius: 6px;
    background: #4caf50;
    color: #fff;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.95rem;
">
  수목 생육 정보 입력
</a>
"""

# DT0001에 있는 "구글폼 자동 채우기 & 열기 스크립트"
SCRIPT_SNIPPET = """
<!-- ===== 구글폼 자동 채우기 & 열기 스크립트 ===== -->
<script>
  window.addEventListener('DOMContentLoaded', function () {
    // 페이지 열릴 때 localStorage 값 불러오기
    if (typeof loadHeaderInfo === 'function') {
      loadHeaderInfo();
    }

    // ① 구글폼 기본 URL
    const FORM_BASE_URL =
      'https://docs.google.com/forms/d/e/1FAIpQLSdcgui0V9bKAUtyOAot7AoysT4UWBrrIkbICbgWIrDZjaaOpA/viewform';

    // ② 각 질문에 해당하는 entry 코드
    const ENTRY_PARK_NAME   = 'entry.1291403664';  // 공원명
    const ENTRY_SURVEYOR    = 'entry.2066724387';  // 조사자명
    const ENTRY_SURVEY_DATE = 'entry.2016295766';  // 조사일자
    const ENTRY_TREE_CODE   = 'entry.1870322508';  // 관리번호(수목코드)

    const btn = document.getElementById('openFormBtn');
    if (!btn) return;

    btn.addEventListener('click', function (e) {
      e.preventDefault(); // 기존 링크 이동 막기

      const parkName   = document.getElementById('parkName').value.trim();
      const surveyor   = document.getElementById('surveyorName').value.trim();
      const surveyDate = document.getElementById('surveyDate').value; // YYYY-MM-DD
      const treeCode   = document.getElementById('treeCode').value;

      if (!parkName || !surveyor || !surveyDate) {
        alert('공원명, 조사자명, 조사일자를 먼저 입력해 주세요.');
        return;
      }

      const params = new URLSearchParams();
      params.set(ENTRY_PARK_NAME,   parkName);
      params.set(ENTRY_SURVEYOR,    surveyor);
      params.set(ENTRY_SURVEY_DATE, surveyDate);
      params.set(ENTRY_TREE_CODE,   treeCode);

      const finalUrl = FORM_BASE_URL + '?' + params.toString();
      window.open(finalUrl, '_blank');
    });
  });
</script>
"""

def main():
  if not os.path.isdir(TARGET_DIR):
    print("대상 폴더를 찾을 수 없습니다:", TARGET_DIR)
    return

  files = sorted(
    f for f in os.listdir(TARGET_DIR)
    if f.startswith("DT") and f.endswith(".html")
  )

  if not files:
    print("처리할 DTxxxx.html 파일이 없습니다.")
    return

  added_button = 0
  skipped_button = 0
  added_script = 0
  skipped_script = 0

  for fname in files:
    path = os.path.join(TARGET_DIR, fname)

    with open(path, "r", encoding="utf-8") as f:
      html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # ─────────────────────────────
    # 1) "생육 및 관리 상태" 섹션 아래에 버튼 추가
    # ─────────────────────────────
    if soup.find(id="openFormBtn"):
      skipped_button += 1
    else:
      # h2 중에서 "생육 및 관리 상태" 찾기
      target_h2 = None
      for h in soup.find_all("h2"):
        if "생육 및 관리 상태" in h.get_text(strip=True):
          target_h2 = h
          break

      if target_h2:
        # h2 다음에 나오는 p(설명문) 뒤에 버튼 블록 삽입
        p = target_h2.find_next("p")
        insert_pos = p if p else target_h2

        snippet_nodes = BeautifulSoup(BUTTON_SNIPPET, "html.parser")
        last_node = insert_pos
        for node in list(snippet_nodes.children):
          if str(node).strip():
            last_node.insert_after(node)
            last_node = node

        added_button += 1
      else:
        print(f"[{fname}] ▶ '생육 및 관리 상태' 섹션을 찾지 못해서 버튼을 추가하지 못했습니다.")

    # ─────────────────────────────
    # 2) 폼 전송 스크립트 추가 (이미 있으면 생략)
    # ─────────────────────────────
    if "FORM_BASE_URL" in html and "ENTRY_PARK_NAME" in html and "openFormBtn" in html:
      skipped_script += 1
    else:
      if soup.body:
        script_nodes = BeautifulSoup(SCRIPT_SNIPPET, "html.parser")
        soup.body.append(script_nodes)
        added_script += 1
      else:
        print(f"[{fname}] ▶ <body> 태그를 찾지 못해서 스크립트를 추가하지 못했습니다.")

    # 변경 내용을 다시 파일에 저장
    with open(path, "w", encoding="utf-8") as f:
      f.write(str(soup))

  print("=== 처리 결과 ===")
  print(f"버튼 추가: {added_button}개, 버튼 건너뜀(이미 존재): {skipped_button}개")
  print(f"스크립트 추가: {added_script}개, 스크립트 건너뜀(이미 존재): {skipped_script}개")

if __name__ == "__main__":
  main()