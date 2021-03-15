import logging 
import csv
import collections
from re import search

import requests
import bs4





from  google_spread import GoogleTable

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('wb')
ParseResult =  collections.namedtuple(
    'Parsedesult',
    (
        'brand_name',
        'goods_name',
        'url',
        'price'
    )
)

HEADER = ("Бренд", "Товар","Ссылка" ,"Цена")

class GoodParcer():
    def __init__(self, url):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36",
            'Acccept-Language' :'ru'
        }
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

        #logger.info(soup)

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
            'Acccept-Language' :'ru'
        }
        self.url = url
        self.result = []
        self.parsed_items = 0

    def load_page(self,   page = 1 ):
        res = self.session.get(self.url+f"&page={page}")
        res.raise_for_status()

        return res.text

    def parse_page(self, text):
        soup = bs4.BeautifulSoup(text, "lxml")
        container = soup.select("div.dtList.i-dtList.j-card-item") 
        for block in container:
            if self.parse_block(block):
                self.parsed_items += 1
        



    def save_csv(self,fname='results.csv'):
        with open(fname,'w', encoding='utf-16', newline="") as f:
            writer = csv.writer(f)
            writer.writerow((h for h in HEADER))
            for row in self.result:
                writer.writerow(cell for cell in row)  
                    

    def save_google(self,name="Wildberries.Pijamas"):
        table = GoogleTable(docname=name,headers=HEADER)
        table.add_rows(self.result)


    def parse_block(self, block):
        logger.info("="*80)

        url_block = block.select_one('a.ref_goods_n_p.j-open-full-product-card')

        url = ("https://www.wildberries.ru" + url_block.get('href')).replace("?targetUrl=GP","")
        logger.info(url)

        brand_block = block.select_one('div.dtlist-inner-brand-name')


        goods_block = brand_block.select_one('span.goods-name')
        goods = goods_block.text
        
        logger.info("Товар: \t %s", goods_block.text)

        brand = brand_block.select_one('strong.brand-name').text.replace('/',"").strip()
        logger.info("Бренд: \t %s", brand)

        price_block = block.select_one('div.j-cataloger-price').select_one('ins.lower-price')
        if not price_block:
            logger.error("Not a price block")
            return False
        logger.info("Цена: \t %s", price_block.text)

        def price_to_int(price:str)->int:
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

client = GoodParcer("https://www.wildberries.ru/catalog/14816271/detail.aspx")

