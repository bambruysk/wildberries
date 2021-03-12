import requests
import bs4

import logging 
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('wb')

class Client():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36",
            'Acccept-Language' :'ru'
        }

    def load_page(self, page = None ):
        url = "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/odezhda-dlya-doma"
        res = self.session.get(url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text):
        soup = bs4.BeautifulSoup(text, "lxml")
        container = soup.select("div.dtList.i-dtList.j-card-item.j-advert-card-item.advert-card-item") 
        for block in container:
            self.parse_block(block)


    def parse_block(self, block):
        logger.info(block)
        logger.info("="*80)

    def run(self):
        page = self.load_page()
        self.parse_page(page)

client = Client()

client.run()