import os
import time
import base64
import requests
import hashlib
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

class PlaywrightCore:
    def __init__(self, page: Page):
        self.page = page
        self.seen_hashes = set()

    def navigate(self, url: str):
        self.page.goto(url)

    def type_text(self, xpath: str, text: str):
        self.page.locator(f"xpath={xpath}").fill(text)

    def press_key(self, key: str):
        self.page.keyboard.press(key)

    def wait_for_element(self, xpath: str, timeout: int = 5000):
        try:
            self.page.locator(f"xpath={xpath}").wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def scroll_to_bottom(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def get_elements(self, xpath: str):
        return self.page.locator(f"xpath={xpath}").all()

    def _download_content(self, src: str):
        """Baixa o conteúdo, seja URL ou Base64, com Headers para evitar bloqueio."""
        try:
            # Caso Base64
            if src.startswith("data:image"):
                header, encoded = src.split(",", 1)
                ext = header.split(";")[0].split("/")[1]
                if ext == "jpeg": ext = "jpg"
                return base64.b64decode(encoded), ext

            # Caso URL Http
            elif src.startswith("http"):
                # HEADERS SÃO CRUCIAIS AQUI
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                response = requests.get(src, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.content, "jpg" # Assume jpg se não souber
        except Exception as e:
            print(f"Erro no download: {e}")
        
        return None, None

    def save_image(self, src: str, folder: str, prefix: str) -> bool:
        if not src: return False

        content, ext = self._download_content(src)
        
        # Filtra imagens vazias ou muito pequenas (< 2KB)
        if not content or len(content) < 2500:
            return False

        # Hash para evitar duplicatas
        file_hash = hashlib.md5(content).hexdigest()
        if file_hash in self.seen_hashes:
            return
        
        self.seen_hashes.add(file_hash)

        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = os.path.join(folder, f"{prefix}_{file_hash}.{ext}")
        
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                f.write(content)
            print(f"[SALVO] {filename}")
            return True # Retorna Sucesso
        
        return False # Já existia, não salvou