import requests
import bs4

import  csv

import collections

import logging 

from selenium import webdriver
from  google_spread import GoogleTable
from selenium.webdriver.common.keys import Keys



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

HOST =  "www.wildberries.ru"

page_url = "https://www.wildberries.ru/catalog/9046503/detail.aspx"


driver =  webdriver.Chrome("C:\chromedriver\chromedriver.exe",)
driver.get(page_url)
element  = driver.find_element_by_name("order-quantity")

logger.info(element)




logging.info(driver)

driver.close()
