from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter


class ComickClient(MangaClient):

    base_url = urlparse("https://comick.io/")
    search_url = base_url.geturl() 
    search_param = 'q'
    updates_url = base_url.geturl()

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, name="Comick", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        cards = bs.findAll("div", {"class": "group flex flex-col"})
        
        mangas = [card.findNext('a') for card in cards]
        names = [manga.find("h2").text.strip() for manga in mangas]
        url = [self.base_url.geturl() + manga.get("href").strip('/') for manga in mangas]
        images = [manga.findNext("img").get("src") for manga in mangas]

        mangas = [MangaCard(self, *tup) for tup in zip(names, url, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        container = bs.find("div", {"class": "overflow-hidden"})
        items = container.find_all("a", {"class": "grid grid-cols-1"})
        
        links = [self.base_url.geturl() + item.get("href").strip('/') for item in items]
        texts = [item.find("span", {"class": "text-sm"}).text.strip() for item in items]

        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    async def updates_from_page(self, content):
        bs = BeautifulSoup(content, "html.parser")

        manga_items = bs.find_all("div", {"class": "relative flex flex-col"})

        urls = dict()

        for manga_item in manga_items:
            manga_url = self.base_url.geturl() + manga_item.findNext("a").get("href").strip('/')
            
            if manga_url in urls:
                continue
            
            data = await self.get_url(manga_url)
            bs = BeautifulSoup(data.text, "html.parser")
            chapter_link = bs.find("a", {"class": "grid grid-cols-1"})
            if chapter_link:
                chapter_url = self.base_url.geturl() + chapter_link.get("href").strip('/')
                urls[manga_url] = chapter_url

        return urls

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")

        container = bs.find("div", {"class": "flex flex-col items-center"})
        images = container.find_all("img") if container else []

        images_url = [quote(img.get("src"), safe=':/%') for img in images if img.get("src")]
        
        return images_url

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = quote_plus(query)

        request_url = self.search_url + "search"

        if query:
            request_url += f'?{self.search_param}={query}'

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
        content = await self.get_url(self.updates_url)

        updates = await self.updates_from_page(content)

        updated = []
        not_updated = []
        for lc in last_chapters:
            if lc.url in updates.keys():
                if updates.get(lc.url) != lc.chapter_url:
                    updated.append(lc.url)
            elif updates.get(lc.url) == lc.chapter_url:
                not_updated.append(lc.url)
                
        return updated, not_updated