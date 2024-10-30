from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus
from bs4 import BeautifulSoup
from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter


class OmegaScansClient(MangaClient):

    base_url = urlparse("https://omegascans.org/")
    search_url = urljoin(base_url.geturl(), "search")
    updates_url = base_url.geturl() 

    pre_headers = {
        'User -Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    def __init__(self, *args, name="OmegaScans", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")
        manga_grid = bs.find("div", {"class": "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5"})
        if not manga_grid:
            return []

        manga_cards = manga_grid.find_all("div", {"class": "border border-primary-100/20"})
        mangas = []
        
        for card in manga_cards:
            try:
                link_tag = card.find("a", {"class": "text-white"})
                name = link_tag.text.strip()
                url = link_tag.get("href")
                img = card.find("img")
                image = img.get("src") if img else ""

                mangas.append(MangaCard(self, name, url, image))
            except Exception as e:
                print(f"Error parsing manga card: {e}")
                continue

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")
        chapter_list = bs.find("div", {"class": "border-t border-t-primary-100/20"})
        if not chapter_list:
            return []

        chapters = []
        chapter_items = chapter_list.find_all("a", {"class": "block"})

        for item in chapter_items:
            try:
                chapter_title = item.find("p", {"class": "text-lg"}).text.strip()
                chapter_url = item.get("href")
                chapters.append(MangaChapter(self, chapter_title, chapter_url, manga, []))
            except Exception as e:
                print(f"Error parsing chapter: {e}")
                continue

        return chapters

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")
        reader = bs.find("div", {"class": "max-w-5xl mx-auto"})
        if not reader:
            return []

        images = reader.find_all("img", {"class": "chapter-img"})
        images_url = []

        for img in images:
            src = img.get("data-src") or img.get("src")
            if src:
                images_url.append(quote(src, safe=':/%'))

        return images_url

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = quote_plus(query)
        request_url = f"{self.search_url}?keyword={query}" if query else self.base_url.geturl()
        content = await self.get_url(request_url)
        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:
        content = await self.get_url(manga_card.url)
        chapters = self.chapters_from_page(content, manga_card)
        return chapters[(page - 1) * 20:page * 20]

    async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')
        content = await self.get_url(manga_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def updates_from_page(self, content):
        bs = BeautifulSoup(content, "html.parser")
 latest_grid = bs.find("div", {"class": "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5"})
        if not latest_grid:
            return {}

        urls = {}
        manga_items = latest_grid.find_all("div", {"class": "border border-primary-100/20"})

        for item in manga_items:
            try:
                manga_link = item.find("a", {"class": "text-white"})
                if not manga_link:
                    continue

                manga_url = manga_link.get("href")
                if manga_url in urls:
                    continue

                chapter_link = item.find("a", {"class": "text-primary-300"})
                if chapter_link:
                    chapter_url = chapter_link.get("href")
                    urls[manga_url] = chapter_url
            except Exception as e:
                print(f"Error parsing updates: {e}")
                continue

        return urls

    async def check_updated_urls(self, last_chapters: List[LastChapter]):
        content = await self.get_url(self.updates_url)
        updates = await self.updates_from_page(content)

        updated = []
        not_updated = []

        for lc in last_chapters:
            if lc.url in updates:
                if updates[lc.url] != lc.chapter_url:
                    updated.append(lc.url)
                else:
                    not_updated.append(lc.url)
            else:
                not_updated.append(lc.url)

        return updated, not_updated