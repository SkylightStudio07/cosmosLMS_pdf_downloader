# cosmosLMS_pdf_downloader

cosmos LMS에 올라와 있는 PDF 이미지를 자동으로 다운로드하여 PDF로 변환해주는 도구.

---

# 사용법

## ✓ 1. 라이브러리 설치

```
pip install -r requirements.txt
```

크롬 드라이버는 **자동으로 설치**되므로 별도로 받을 필요 없음.

## ✓ 2. 실행

**`run.bat` 더블클릭** → GUI 창이 열림.

또는 터미널에서:

```
python gui.py
```

## ✓ 3. GUI 사용

1. **URL 입력창**에 다운로드할 URL을 붙여넣기 (여러 개는 줄바꿈으로 구분)
2. **저장 경로** 확인 (기본값: `./downloads`)
3. **▶ 다운로드 시작** 클릭
4. 로그창에서 진행 상황 확인
5. 완료 후 저장 경로에서 PDF 확인

## ✓ 4. config.ini (선택)

저장 경로 기본값은 `config.ini`에서 변경 가능.

```ini
[DEFAULT]
# 이미지파일 저장 경로 (마지막 / 제외하고)
SAVE_PATH = ./downloads
```

---

# 라이브러리

| 패키지 | 용도 |
|---|---|
| `bs4` | HTML 파싱 |
| `selenium` | 웹 자동화 |
| `webdriver-manager` | ChromeDriver 자동 설치/관리 |
| `img2pdf` | 이미지 → PDF 변환 |

표준 라이브러리(`urllib`, `os`, `time`, `configparser`, `tkinter`)는 별도 설치 불필요.

---
