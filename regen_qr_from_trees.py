import re
from pathlib import Path
import qrcode

TREES_DIR = Path("trees")               # HTML 폴더
QR_DIR = Path("qr")                     # QR PNG 저장 폴더
BASE_URL = "https://theforim.com/t/"    # QR에 넣을 주소

PNG_SIZE_BOX = 10
BORDER = 4

def is_valid_code(code: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9-]+", code))

def main():
    if not TREES_DIR.exists():
        raise SystemExit(f"[오류] trees 폴더 없음: {TREES_DIR.resolve()}")

    QR_DIR.mkdir(parents=True, exist_ok=True)

    html_files = sorted(TREES_DIR.glob("*.html"))
    if not html_files:
        raise SystemExit("[오류] trees 폴더에 .html 파일이 없습니다.")

    created = 0
    skipped = 0

    for f in html_files:
        code = f.stem
        if not is_valid_code(code):
            skipped += 1
            continue

        url = BASE_URL + code
        out_path = QR_DIR / f"{code}.png"

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=PNG_SIZE_BOX,
            border=BORDER,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(out_path)

        created += 1

    print("===================================")
    print(f"생성: {created}개")
    print(f"스킵: {skipped}개")
    print(f"저장 위치: {QR_DIR.resolve()}")
    print("===================================")

if __name__ == "__main__":
    main()