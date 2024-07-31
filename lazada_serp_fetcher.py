import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
import os
import urllib.parse
import json
import math
from lazada_serp_fetcher.items import LazadaSerpFetcherItem

class LazadaSerpFetcherrSpider(scrapy.Spider):
    name = 'lazada_serp_fetcher'
    allowed_domains = ['www.lazaada.th']
    start_urls = ['http://www.lazaada.th/']

    def __init__(
        self,
        seeds=None,
        max_pages=None,
    ):
        self.max_pages = max_pages 
        self.headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'bx-v': '2.5.13',
                'priority': 'u=1, i',
                'referer': 'https://www.lazada.co.th/',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'x-csrf-token': 'e5fe5b63b8a39',
            }
        self.seeds = seeds.split("|")

    def start_requests(self):     
        for seed in self.seeds:
            yield from self.fetch_page(seed, 1)

    def fetch_page(self, seed, pg_no):
        cookies = {'cna': 'YJjgHqpdInICActR8WpI6Ycs'}
        params = {
            'ajax': 'true',
            'catalog_redirect_tag': 'true',
            'isFirstRequest': 'true',
            'page': str(pg_no),
            'q': seed,
            'spm': 'a2o4m.homepage.search.d_go',
        }
        url = os.getenv("API_URL")
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        yield scrapy.Request(
            url=full_url,
            headers=self.headers,
            method="GET",
            cookies=cookies,
            callback=self.parse,
            dont_filter=True,
            cb_kwargs={"seed": seed, "pg_no": pg_no},
        )

    def parse(self, response, seed, pg_no):
        json_data = response.json()
        prod_nodes = json_data['mods']['listItems']
        
        for each_prod in prod_nodes:
            loader = self.create_item_loader(each_prod, response, seed,pg_no)
            yield loader.load_item()
        
        total_prods = int(json_data['mods']['filter']['filteredQuatity'])
        total_pages = math.ceil(total_prods / 40)
        
        if int(pg_no) < min(total_pages, int(self.max_pages)):
            pg_no += 1
            yield from self.fetch_page(seed, pg_no)

    def create_item_loader(self, each_prod, response, seed,pg_no):
        loader = ItemLoader(item=LazadaSerpFetcherItem(), response=response)
        rating_str = each_prod.get('ratingScore')
        rating = round(float(rating_str), 2) if rating_str else None
        mrp = each_prod.get('originalPrice') or each_prod.get('price')
        images = [img.get('image') for img in each_prod.get('thumbs', [])]
        loader.add_value('sku', each_prod.get('sku'))
        loader.add_value('reviews_count', each_prod.get('review'))
        loader.add_value('product_url', each_prod.get('itemUrl'))
        loader.add_value('merchant_name', each_prod.get('sellerName'))
        loader.add_value('seller_id', each_prod.get('sellerId'))
        loader.add_value('title', each_prod.get('name'))
        loader.add_value('keyword', seed)
        loader.add_value('thumbnail', each_prod.get('image'))
        loader.add_value('brand', each_prod.get('brandName'))
        loader.add_value('price', each_prod.get('price'))
        loader.add_value('rating', rating)
        loader.add_value('discount', each_prod.get('discount'))
        loader.add_value('mrp', mrp)
        loader.add_value('page_number',pg_no)
        loader.add_value('images',images)
        loader.add_value('sponsored', each_prod.get('isSponsored'))
        loader.add_value('item_id', each_prod.get('itemId'))
        loader.add_value('in_stock', each_prod.get('inStock'))
        loader.add_value('sold_count', each_prod.get('itemSoldCntShow'))     
        return loader