import asyncio
from api.collector.core.basic_async_crawler import BaseAsyncCrawler
from parsel import Selector
from api.logger import logger


class JDSClient(BaseAsyncCrawler):
    def get_pdf_links(self, html_content: str) -> list:
        sel = Selector(text=html_content)
        articles_data = []

        # O container principal enviado é .search__item__body
        containers = sel.css(".search__item__body")

        for item in containers:
            # 1. Título Limpo (Ignora spans de highlight)
            title = item.xpath("string(.//h2[@class='meta__title']/a)").get()

            # 2. Link Direto do PDF (Usa a classe pdf-link que você enviou)
            pdf_link = item.css("a.pdf-link::attr(href)").get()

            if title and pdf_link:
                # Normaliza link se for relativo
                full_url = (
                    pdf_link
                    if pdf_link.startswith("http")
                    else f"https://www.journalofdairyscience.org{pdf_link}"
                )
                articles_data.append((full_url, title.strip()))

        return articles_data

    def get_next_page(self, html_content: str) -> str | None:
        sel = Selector(text=html_content)

        # Seletor robusto: procura a tag 'a' que envolve o ícone de próxima página
        # O XPath '..' sobe um nível do ícone para pegar o href do link pai
        next_path = sel.css("a.pagination__btn--next::attr(href)").get()

        if next_path:
            full_url = (
                f"https://www.journalofdairyscience.org{next_path}"
                if next_path.startswith("/")
                else next_path
            )
            logger.info(f"Próxima página encontrada: {full_url}")
            return full_url

        logger.info("Fim da paginação (última página atingida).")
        return None


if __name__ == "__main__":
    # Exemplo: Pesquisa sobre produção de leite (dairy production) no MDPI
    busca_url = "https://www.journalofdairyscience.org/search?q=milk production"

    crawler = JDSClient(
        base_url="https://www.journalofdairyscience.org",
        output_dir="artigos_milk_production",
    )
    asyncio.run(crawler.run(busca_url))
