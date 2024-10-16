from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter

class FlamesComicClient(MangaClient):
    base_url = urlparse("https://flamescomic.org/")
    search_url = base_url.geturl()
    search_param = 's'
    updates_url = base_url.geturl()

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, name="FlamesComic", headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        container = bs.find("div", {"class": "row mx-0"})
        cards = container.find_all("div", {"class": "col-md-3 col-6"})

        names = [card.find("h4", {"class": "card-title"}).string.strip() for card in cards]
        urls = [urljoin(self.base_url.geturl(), card.find("a").get("href")) for card in cards]
        images = [card.find("img").get("src") for card in cards]

        mangas = [MangaCard(self, *tup) for tup in zip(names, urls, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        chapters = bs.find_all("div", {"class": "chapter-list"})

        links = [urljoin(self.base_url.geturl(), chapter.find("a").get("href")) for chapter in chapters]
        texts = [chapter.find("span", {"class": "chapter-title"}).string.strip() for chapter in chapters]

        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")

        container = bs.find("div", {"class": "chapter-content"})

        images_url = [quote(img.get("src"), safe=':/%') for img in container.find_all("img")]

        return images_url

    @staticmethod
    def updates_from_page(page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        manga_items = bs.find_all("div", {"class": "col-md-3 col-6"})

        urls = dict()

        for manga_item in manga_items:
            manga_url = urljoin(FlamesComicClient.base_url.geturl(), manga_item.find("a").get("href"))

            if manga_url in urls:
                continue

            chapter_url = urljoin(FlamesComicClient.base_url.geturl(), manga_item.find("a", {"class": "chapter-link"}).get("href"))

            urls[manga_url] = chapter_url

        return urls

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = quote_plus(query)

        request_url = self.search_url

        if query:
            request_url += f'search/?search={query}'

        content = await self.get_url(request_url)

        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1)
