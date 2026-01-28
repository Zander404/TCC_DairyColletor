import asyncio
from api.collector.core.basic_async_crawler import BaseAsyncCrawler
from parsel import Selector
from api.logger import logger


class MDPIClient(BaseAsyncCrawler):
    def get_pdf_links(self, html_content: str) -> list:
        sel = Selector(text=html_content)
        articles_data = []

        # Captura todos os blocos de artigos
        containers = sel.css(".article-content")

        for item in containers:
            # 1. Extração do Título: usamos xpath('string(...)') para pegar
            # o texto de todas as tags internas (como <i> ou <b>) de uma vez.
            title = item.xpath("string(.//a[@class='title-link'])").get()

            # 2. Extração do Link do PDF
            pdf_link = item.css("a[href*='/pdf']::attr(href)").get()

            if title and pdf_link:
                # Limpeza de espaços extras e normalização do link
                clean_title = title.strip()
                full_pdf_url = pdf_link.strip()
                if not full_pdf_url.startswith("http"):
                    full_pdf_url = f"https://www.mdpi.com{full_pdf_url}"

                articles_data.append((full_pdf_url, clean_title))
                logger.info(f"Encontrado: {clean_title[:50]}...")

        return articles_data

    def get_next_page(self, html_content: str) -> str | None:
        sel = Selector(text=html_content)

        # Seletor robusto: procura a tag 'a' que envolve o ícone de próxima página
        # O XPath '..' sobe um nível do ícone para pegar o href do link pai
        next_path = sel.xpath(
            "//i[contains(text(), 'chevron_right')]/parent::a/@href"
        ).get()

        if next_path:
            full_url = (
                f"https://www.mdpi.com{next_path}"
                if next_path.startswith("/")
                else next_path
            )
            logger.info(f"Próxima página encontrada: {full_url}")
            return full_url

        logger.info("Fim da paginação (última página atingida).")
        return None


if __name__ == "__main__":
    # Exemplo: Pesquisa sobre produção de leite (dairy production) no MDPI
    busca_url = "https://www.mdpi.com/search?q=milk production"

    crawler = MDPIClient(
        base_url="https://www.mdpi.com", output_dir="artigos_milk_production"
    )
    asyncio.run(crawler.run(busca_url))
