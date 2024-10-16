from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter

class FlamesComicClient(MangaClient):
    base_url = urlparse("https://flamescomics.xyz/")
    search_url = urljoin(base_url.geturl(), "search")
    updates_url = base_url.geturl()

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, name="FlamesComic", headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        containers = bs.find_all("div", {"class": "bsx"})

        names = [container.find("div", {"class": "tt"}).text.strip() for container in containers]
        urls = [container.find("a").get("href") for container in containers]
        images = [container.find("img").get("src") for container in containers]

        mangas = [MangaCard(self, *tup) for tup in zip(names, urls, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        chapters = bs.find("div", {"id": "chapterlist"}).find_all("li")

        links = [chapter.find("a").get("href") for chapter in chapters]
        texts = [chapter.find("span", {"class": "chapternum"}).text.strip() for chapter in chapters]

        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")

        container = bs.find("div", {"id": "readerarea"})

        images_url = [quote(img.get("src"), safe=':/%') for img in container.find_all("img") if img.get("src")]

        return images_url

    def updates_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        manga_items = bs.find_all("div", {"class": "bsx"})

        urls = dict()

        for manga_item in manga_items:
            manga_url = manga_item.find("a").get("href")

            if manga_url in urls:
                continue

            chapter_url = manga_item.find("div", {"class": "epxs"}).find("a").get("href")

            urls[manga_url] = chapter_url

        return urls

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = quote_plus(query)

        request_url = f"{self.search_url}?s={query}&post_type=wp-manga"

        content = await self.get_url(request_url)

        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:
        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        return self.chapters_from_page(content, manga_card)[(page - 1) * 20:page * 20]

     async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def check_updated_urls(self, last_chapters: List[LastChapter]):
        page = await self.get_url(self.updates_url)
        
        updates = await self.updates_from_page(page)
        
        updated = []
        not_updated = []
        for lc in last_chapters:
            if lc.url in updates.keys():
                if updates.get(lc.url) != lc.chapter_url:
                    updated.append(lc.url)
                elif updates.get(lc.url) == lc.chapter_url:
                    not_updated.append(lc.url)
                
        return updated, not_updated
