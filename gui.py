import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import configparser
import os
from time import sleep
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import img2pdf


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CosmosLMS PDF Downloader")
        self.geometry("720x640")
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")

        # config 읽기
        self.cf = configparser.ConfigParser()
        self.cf.read("config.ini", encoding="utf-8")

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("맑은 고딕", 14, "bold"), background="#f0f0f0")
        style.configure("TButton", font=("맑은 고딕", 10), padding=6)
        style.configure("TLabel", background="#f0f0f0", font=("맑은 고딕", 10))
        style.configure("TFrame", background="#f0f0f0")

        main = ttk.Frame(self, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # 제목
        ttk.Label(main, text="CosmosLMS PDF Downloader", style="Title.TLabel").pack(anchor=tk.W, pady=(0, 12))

        # URL 입력
        ttk.Label(main, text="다운로드할 URL (한 줄에 하나씩):").pack(anchor=tk.W)
        url_frame = ttk.Frame(main)
        url_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 10))
        self.url_text = scrolledtext.ScrolledText(url_frame, height=7, font=("Consolas", 10), relief="solid", bd=1)
        self.url_text.pack(fill=tk.BOTH, expand=True)

        # 기존 download_list 불러오기
        try:
            with open("download_list", "r") as f:
                content = f.read().strip()
                if content:
                    self.url_text.insert(tk.END, content)
        except Exception:
            pass

        # 저장 경로
        path_frame = ttk.Frame(main)
        path_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(path_frame, text="저장 경로:").pack(side=tk.LEFT)
        self.save_path_var = tk.StringVar(value=self.cf["DEFAULT"].get("SAVE_PATH", "./downloads"))
        ttk.Entry(path_frame, textvariable=self.save_path_var, font=("맑은 고딕", 10)).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )
        ttk.Button(path_frame, text="찾아보기", command=self._browse_path).pack(side=tk.LEFT)

        # 버튼
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 8))
        self.start_btn = ttk.Button(btn_frame, text="▶  다운로드 시작", command=self._start_download)
        self.start_btn.pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="로그 지우기", command=self._clear_log).pack(side=tk.LEFT, padx=8)

        # 상태 + 진행바
        self.status_var = tk.StringVar(value="대기 중")
        ttk.Label(main, textvariable=self.status_var, foreground="#555").pack(anchor=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main, variable=self.progress_var, maximum=100, length=400)
        self.progress.pack(fill=tk.X, pady=(4, 8))

        # 로그
        ttk.Label(main, text="로그:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(
            main, height=12, font=("Consolas", 9), state=tk.DISABLED, relief="solid", bd=1, bg="#1e1e1e", fg="#d4d4d4"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("ok", foreground="#4ec9b0")
        self.log_text.tag_config("err", foreground="#f44747")
        self.log_text.tag_config("info", foreground="#9cdcfe")

    def _browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path_var.set(path)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log(self, msg, tag=None):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n", tag or "")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.update_idletasks()

    def _start_download(self):
        urls = [u.strip() for u in self.url_text.get("1.0", tk.END).splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning("경고", "URL을 입력해주세요.")
            return
        # download_list 파일도 업데이트
        with open("download_list", "w") as f:
            f.write("\n".join(urls))

        self.start_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        threading.Thread(target=self._run_download, args=(urls,), daemon=True).start()

    def _run_download(self, url_list):
        for idx, url in enumerate(url_list):
            self.status_var.set(f"[{idx+1}/{len(url_list)}] 처리 중...")
            self._log(f"\n{'='*50}", "info")
            self._log(f"[{idx+1}/{len(url_list)}] {url}", "info")
            try:
                self._download_url(url, self.save_path_var.get())
            except Exception as e:
                self._log(f"오류: {e}", "err")
            self.progress_var.set((idx + 1) / len(url_list) * 100)

        self.status_var.set("✔  모든 다운로드 완료!")
        self._log("\n모든 작업이 완료되었습니다.", "ok")
        self.start_btn.config(state=tk.NORMAL)

    def _download_url(self, url, save_path):
        self._log("크롬 드라이버 시작 중...", "info")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        try:
            driver.get(url)
            driver.implicitly_wait(10)
            sleep(3)
            driver.switch_to.frame("docFrame")
            sleep(3)

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            title_el = soup.select_one(".fnm")
            if not title_el:
                self._log("문서 제목을 찾을 수 없습니다. URL을 확인해주세요.", "err")
                return
            title = title_el.text.strip()
            self._log(f"제목: {title}", "ok")

            dir_path = os.path.join(save_path, title)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # 이미지 수집
            img_list = []
            i = 0
            while True:
                try:
                    thumb_id = soup.select_one("#thumb" + str(i)).attrs["id"]
                    driver.find_element(By.ID, thumb_id).click()
                    sleep(1)
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    page = soup.select_one("#page" + str(i))
                    img_url = "https://doc.coursemos.co.kr" + page.attrs["src"]
                    img_list.append(img_url)
                    self._log(f"  페이지 {i+1} 발견")
                    i += 1
                except AttributeError:
                    break

            if not img_list:
                self._log("이미지를 찾지 못했습니다. 페이지 구조가 다를 수 있습니다.", "err")
                return

            self._log(f"총 {len(img_list)}페이지 다운로드 시작...", "info")

            # 이미지 저장
            img_save_path = []
            for i, img_url in enumerate(img_list):
                self._log(f"  이미지 {i+1}/{len(img_list)} 다운로드 중...")
                img_path = os.path.join(dir_path, f"{title}_{i}.png")
                urlretrieve(img_url, img_path)
                img_save_path.append(img_path)

            # PDF 변환
            self._log("PDF 변환 중...", "info")
            load_image = []
            for img_path in img_save_path:
                with open(img_path, "rb") as f:
                    load_image.append(f.read())
            pdf_path = os.path.join(dir_path, f"{title}.pdf")
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(img2pdf.convert(load_image))

            self._log(f"저장 완료: {pdf_path}", "ok")

        finally:
            driver.quit()


if __name__ == "__main__":
    app = App()
    app.mainloop()
