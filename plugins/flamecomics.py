class FlamesComicClient(MangaClient):
    base_url = urlparse("https://flamescomic.org/")
    search_url = base_url.geturl()
    search_param = 's'
    updates_url = base_url.geturl()

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        # Updated container and card selectors
        container = bs.find("div", {"class": "row mx-0"})
        cards = container.find_all("div", {"class": "col-md-3 col-6"})

        # Updated name, url, and image selectors
        names = [card.find("h4", {"class": "card-title"}).string.strip() for card in cards]
        urls = [urljoin(self.base_url.geturl(), card.find("a").get("href")) for card in cards]
        images = [card.find("img").get("src") for card in cards]

        mangas = [MangaCard(self, *tup) for tup in zip(names, urls, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        # Updated chapter selectors
        chapters = bs.find_all("div", {"class": "chapter-list"})

        # Updated link and text selectors
        links = [urljoin(self.base_url.geturl(), chapter.find("a").get("href")) for chapter in chapters]
        texts = [chapter.find("span", {"class": "chapter-title"}).string.strip() for chapter in chapters]

        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")

        # Updated image container selector
        container = bs.find("div", {"class": "chapter-content"})

        # Updated image selectors
        images_url = [quote(img.get("src"), safe=':/%') for img in container.find_all("img")]

        return images_url

    async def updates_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        # Updated manga item selectors
        manga_items = bs.find_all("div", {"class": "col-md-3 col-6"})

        urls = dict()

        for manga_item in manga_items:
            manga_url = urljoin(self.base_url.geturl(), manga_item.find("a").get("href"))

            if manga_url in urls:
                continue

            chapter_url = urljoin(self.base_url.geturl(), manga_item.find("a", {"class": "chapter-link"}).get("href"))

            urls[manga_url] = chapter_url

        return urls
