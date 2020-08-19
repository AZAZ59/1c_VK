# Scrapy settings for lcwaikiki project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'lcwaikiki'

SPIDER_MODULES = ['lcwaikiki.spiders']
NEWSPIDER_MODULE = 'lcwaikiki.spiders'

DOWNLOAD_TIMEOUT = 10
RETRY_TIMES = 10

CSV_DELIMITER = ';'

FEED_EXPORTERS = {
    'csv': 'lcwaikiki.middlewares.MyProjectCsvItemExporter',
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.86 YaBrowser/20.8.0.903 Yowser/2.5 Safari/537.36'
HTTPERROR_ALLOWED_CODES =[200,403]

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  'cookie': "ResesAuth=1; visitorId=7ec00852-77aa-4fad-b703-9dd3a653bf6a; _gcl_au=1.1.1598195813.1596111831; _ga=GA1.2.601040263.1596111833; _fbp=fb.1.1596111833841.218573242; scarab.visitor=%2266A161577D054D2D%22; scarab.profile=%220SO325Z4%252DCRK%7C1596461384%22; __cfduid=dee7e00d447b39bed29ef557bf7fc4e2b1597665487; ASP.NET_SessionId=nlzyp2fc0aknmb0o5sq1co2j; guestSessionId=d371f3ac-f769-4190-abb7-3084d192c16e; undefined=-1; _gid=GA1.2.1056430344.1597665544; _hjid=fe5e771b-d778-4296-b749-cd8b60c480a6; ins-customer-id=; _hjDonePolls=525838%2C524803%2C527213; TLTSID=DND; scarab.mayAdd=%5B%7B%22i%22%3A%220W0049Z4-PTE%22%7D%5D; insLastVisitedProd=%7B%22id%22%3A%220W0049Z4_684705%22%2C%22name%22%3A%22K%C4%B1z%20%C3%87ocuk%20Kap%C3%BC%C5%9Fonlu%20Mont%22%2C%22price%22%3A199.99%2C%22originalPrice%22%3A199.99%2C%22cats%22%3A%5B%22Cocuk%22%2C%22Kiz%20Cocuk%22%2C%22Mont%20ve%20Kaban-Kiz%20Cocuk%22%5D%2C%22img%22%3A%22https%3A%2F%2Fimg-lcwaikiki.mncdn.com%2Fmnresize%2F320%2F-%2Fpim%2Fproductimages%2F20202%2F3975885%2Fl_20202-0w0049z4-pte_a.jpg%22%2C%22time%22%3A1597665757%2C%22url%22%3A%22https%3A%2F%2Fwww.lcwaikiki.com%2Ftr-TR%2FTR%2Furun%2FLC-WAIKIKI%2Fkiz-cocuk%2FMont%2F3975885%2F684705%22%2C%22quantity%22%3A1%2C%22variants%22%3A%5B%5D%7D; cf_clearance=337c2ae301f94047b1c2c4d0e8ec79bbeb393ba2-1597694322-0-1z767b4c74zcb4b349z77b2b486-250; __cf_bm=13a99f2cf47a6a8ac027cbc072a108cc62e6b6e3-1597694327-1800-AWjhCMmY/tp8qGUT+rIJg9B+p5Oyes81swHc9LVuj0DSHjmubaeJ7NnJU+HehTWziy9zxYfcJ+7umGDym5Vww/+Gs+JjIlqDXpIbN1JPGbkkdBWINLxjYa/SzjgDdyqfaiiFFen+1ySshJ9yHgOHaAjAZfMHNDvIqonGa9pFQTfj3i9n2VMhSSwRS5suitXPvA==; _hjIncludedInSessionSample=0; _hjAbsoluteSessionInProgress=1; _gat_UA-21191506-3=1; ins-storage-version=27; ins-visited-categories=%7B%22Yeni%20Sezon%20Cocuk%20Giyim%22%3A%222%22%2C%22%22%3A%221%22%7D; insLastVisitedCategory=; ADRUM=s=1597695089883&r=https%3A%2F%2Fwww.lcwaikiki.com%2Ftr-TR%2FTR%2Fetiket%2Fbebek-sloganli-tulumlar%2F%3F0"
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'lcwaikiki.middlewares.LcwaikikiSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'lcwaikiki.middlewares.LcwaikikiDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'lcwaikiki.pipelines.LcwaikikiPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
