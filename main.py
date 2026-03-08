from scripts.scraper import GoogleImageScraper

def main():
    # Defina o que quer buscar
    queries = ["gato persa", "pastor alemão"]
    max_images = 30 # Quantidade por termo

    # Inicia o scraper (headless=False para ver o navegador abrindo)
    bot = GoogleImageScraper(headless=False)

    try:
        for query in queries:
            bot.scrape(query, limit=max_images)
            
    finally:
        bot.close()

if __name__ == "__main__":
    main()