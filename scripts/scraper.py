import time
from scripts.core import PlaywrightCore
from playwright.sync_api import sync_playwright

class GoogleImageScraper:
    def __init__(self, headless=False):
        self.playwright = sync_playwright().start()
        # headless=False é importante no Google para carregar visualmente as imagens
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.core = PlaywrightCore(self.page)

    def scrape(self, query: str, limit: int = 50, output_folder="dataset"):
        print(f"--- Iniciando busca: {query} ---")
        
        self.core.navigate("https://www.google.com/imghp?hl=pt-BR")
        
        # 1. Realizar a busca
        search_box = "//textarea[@name='q']"
        self.core.wait_for_element(search_box)
        self.core.type_text(search_box, query)
        self.core.press_key("Enter")
        
        # 2. Aguardar o contêiner principal carregar
        # Usamos o ID que você identificou
        main_div_xpath = "//*[@id='rcnt']"
        found = self.core.wait_for_element(main_div_xpath)
        
        if not found:
            print("Erro: Não foi possível encontrar a div de resultados (#rcnt).")
            return

        # 3. Scroll para carregar mais imagens (Lazy Loading)
        print("Rolando a página...")
        # Aumentei o scroll pois o Google carrega poucas imagens de início
        scrolls = int(limit / 10) + 2
        for _ in range(scrolls):
            self.core.scroll_to_bottom()
            time.sleep(2) # Pausa essencial para o navegador baixar as imagens

        # 4. Coletar imagens dentro do #rcnt
        # O '//img' pega todas as imagens descendentes desse ID
        images_xpath = f"{main_div_xpath}//img"
        elements = self.core.get_elements(images_xpath)
        
        print(f"Total de elementos <img> encontrados no container: {len(elements)}")
        
        count = 0
        target_folder = f"{output_folder}/{query.replace(' ', '_')}"

        for el in elements:
            if count >= limit:
                break
            
            # Tenta extrair a URL de diferentes atributos (o Google esconde no data-src às vezes)
            src = el.get_attribute("src")
            data_src = el.get_attribute("data-src")
            data_iurl = el.get_attribute("data-iurl")

            # Prioridade: data-src (geralmente a imagem real carregada via JS) > src normal
            final_src = data_src if data_src else (src if src else data_iurl)

            if final_src:
                # O core.save_image vai filtrar se for muito pequena (< 2kb)
                # Isso evita baixar ícones da interface do Google que caíram no XPath
                success = self.core.save_image(final_src, target_folder, query)
                if success:
                    count += 1
        
        print(f"--- Finalizado: {count} imagens salvas para '{query}' ---")

    def close(self):
        self.browser.close()
        self.playwright.stop()