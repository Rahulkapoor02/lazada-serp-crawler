Serp Crawler using Scrapy
Data points covered like mrp, price, images, discount etc.
to run- scrapy crawl lazada_serp_fetcher -a seeds="laptop|smartphone" -a max_pages=3
This command will scrape search results for "laptop" and "smartphone" and will process up to 3 pages for each keyword.

Key Methods

__init__(self, seeds=None, max_pages=None): Initializes the spider with seeds and max pages.
start_requests(self): Starts the scraping process for each seed.
fetch_page(self, seed, pg_no): Constructs and sends a request for a specific search results page.
parse(self, response, seed, pg_no): Parses the search results and extracts product data.
create_item_loader(self, each_prod, response, seed, pg_no): Loads the extracted product data into an ItemLoader.
