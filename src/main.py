import logging
import csv
import collections
from re import search
import json

import requests
import bs4


from google_spread import GoogleTable

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('wb')
ParseResult = collections.namedtuple(
    'ParsedResult',
    (
        'article'
        'brand_name',
        'goods_name',
        'url',
        'price',
        'orderCount'
    )
)

SESSION_HEADERS = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36",
            'Acccept-Language': 'ru'
        }

HEADER = ("Артикул","Бренд", "Товар", "Ссылка", "Цена", "Продано")


class GoodsPool():
    def __init__(self):
        self.pool = {}


pool = GoodsPool()

class Url():
    def __init__(self,article):
        self.url = f"https://www.wildberries.ru/catalog/{article}/detail.aspx"
    def __str__(self):
        return self.url


class PageContent():
    def __init__(self, url):
        self.session = requests.Session()
        self.session.headers = SESSION_HEADERS
        self.url = url
        self._page = self.session.get(str(url))
        self._page.raise_for_status()

        # debug
        # save page as html
        with open("dump.html", "w", encoding='utf-16') as f:
            f.write(self._page.text)

    def page(self):
        return self._page


class PageData():
    def __init__(self, content):
        self.content = content

        # need find scripts with json
        # for testing load json from file

        # with open("test.json", encoding="utf-8") as jf:
        #     test_json = jf.read()

        self._json_data = json.loads(self.extract_json(content.page().text))

    def extract_json(self, text: str, tag="ssrModel"):
        # find tag
        start = text.find(tag)
        if start < 0:
            logger.error("Tag not found")
            return ""
        parentesis_counter = 1
        found_first = False
        for i in range(start, len(text)):
            if text[i] == "{":
                start = i+1
                break
        else:
            logger.error(f"json not found")
            return
        for i in range(start, len(text)):
            if text[i] == "{":
                parentesis_counter += 1
            elif text[i] == "}":
                parentesis_counter -= 1
            else:
                continue
            if parentesis_counter == 0:
                return text[start-1:i+1]

        logger.error(f"json bad")
        return ""

    def json_data(self):
        return self._json_data


class ProductPage():
    def __init__(self, article):
        self.article = article
        self.url = Url(article)
        self.page_content = PageContent(url)
        self.page_data = PageData(self.page_content)
        self.product_card = self.page_data.json_data()["productCard"]
        self.name = self.product_card["goodsName"]
        self.brand_name = self.product_card["brandName"]
        self.nomenclatures = self.product_card["nomenclatures"]
        self.orderCount = sum([params["ordersCount"]
                               for params in self.nomenclatures.values()])

    def parse_articuls(self):
        articulus = self.nomenclatures.keys()
        for ar in articulus:
            if ar not in pool.pool:
                pool.pool[ar] = ParseResult(
                    brand_name=self.brand_name,
                    goods_name=self.name,
                    url=self.url,
                    price=self.nomenclatures[ar]["sizes"][0]["price"],
                    orderCount=self.nomenclatures[ar]["ordersCount"]
                )
        


class GoodParcer():
    def __init__(self, url):
        self.session = requests.Session()
        self.session.headers = SESSION_HEADERS}
        self.url = url
        self.res = {}

        page = self.session.get(self.url)
        page.raise_for_status()

        logger.info(page.links)

        soup = bs4.BeautifulSoup(page.text, "lxml")
        # container = soup.select("div.dtList.i-dtList.j-card-item")
        """
        //*[@id="container"]/div[1]/div[2]/div[2]/p/span/text()

        """

        # logger.info(soup)

        js_script = soup.find_all('script')
        for j in js_script:
            matchs = search(r'"ordersCount":[0-9]{1,5}', str(js_script))
            if not matchs:
                continue
            orderCount = matchs.group()
            print(''.join(filter(str.isdigit, orderCount)))

        self.buy_count = soup.select_one("p.order-quantity")

        logger.info(self.buy_count)


class CatalogParcer():
    def __init__(self, url):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36",
            'Acccept-Language': 'ru'
        }
        self.url = url
        self.result = []
        self.parsed_items = 0

    def load_page(self,   page=1):
        res = self.session.get(self.url+f"&page={page}")
        res.raise_for_status()

        return res.text

    def parse_page(self, text):
        soup = bs4.BeautifulSoup(text, "lxml")
        container = soup.select("div.dtList.i-dtList.j-card-item")
        for block in container:
            if self.parse_block(block):
                self.parsed_items += 1

    def save_csv(self, fname='results.csv'):
        with open(fname, 'w', encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            writer.writerow((h for h in HEADER))
            for row in self.result:
                writer.writerow(cell for cell in row)

    def save_google(self, name="Wildberries.Pijamas"):
        table = GoogleTable(docname=name, headers=HEADER)
        table.add_rows(self.result)

    def parse_block(self, block):
        logger.info("="*80)

        url_block = block.select_one(
            'a.ref_goods_n_p.j-open-full-product-card')

        url = ("https://www.wildberries.ru" +
               url_block.get('href')).replace("?targetUrl=GP", "")
        logger.info(url)

        brand_block = block.select_one('div.dtlist-inner-brand-name')

        goods_block = brand_block.select_one('span.goods-name')
        goods = goods_block.text

        logger.info("Товар: \t %s", goods_block.text)

        brand = brand_block.select_one(
            'strong.brand-name').text.replace('/', "").strip()
        logger.info("Бренд: \t %s", brand)

        price_block = block.select_one(
            'div.j-cataloger-price').select_one('ins.lower-price')
        if not price_block:
            logger.error("Not a price block")
            return False
        logger.info("Цена: \t %s", price_block.text)

        def price_to_int(price: str) -> int:
            return int("".join((c for c in price if c.isdigit())))

        price = price_to_int(price_block.text)

        self.result.append(
            ParseResult(
                brand_name=brand,
                goods_name=goods,
                url=url,
                price=price
            )
        )
        return True

    def run(self):
        for page_num in range(1000):
            page = self.load_page(page_num)
            self.parse_page(page)
            if self.parsed_items == 0:
                break
            self.parsed_items = 0


# client = CatalogParcer("https://www.wildberries.ru/catalog/zhenshchinam/odezhda/odezhda-dlya-doma?xsubject=162")
# client.run()
# client.save_google()
if __name__ == "__main__":
    page = ProductPage(
        "https://www.wildberries.ru/catalog/14816271/detail.aspx")
    logger.info(page.orderCount)
