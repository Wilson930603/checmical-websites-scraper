# Scrapy settings for flasks project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'flasks'

SPIDER_MODULES = ['flasks.spiders']
NEWSPIDER_MODULE = 'flasks.spiders'

RETRY_HTTP_CODES = [503, 504, 400, 408, 307, 403]
RETRY_TIMES=50 
URLLENGTH_LIMIT=99999
#REDIRECT_ENABLED = False
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'flasks (+http://www.yourdomain.com)'

# Obey robots.txt rules

ROBOTSTXT_OBEY = False
HTTPERROR_ALLOW_ALL = True
CONCURRENT_REQUESTS = 50
CONCURRENT_REQUESTS_PER_DOMAIN = 500000
CONCURRENT_REQUESTS_PER_IP = 16
# REACTOR_THREADPOOL_MAXSIZE = 20 #testing
DEPTH_PRIORITY = 1 
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False
TELNETCONSOLE_ENABLED = True
TELNETCONSOLE_USERNAME = 'a'
TELNETCONSOLE_PASSWORD = 'a'

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'flasks.middlewares.flasksSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   #'flasks.middlewares.flasksDownloaderMiddleware': 543,
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    #  'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
#        #                                                     ^^^
    #  'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #'scrapy_crawlera.CrawleraMiddleware': 610,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'flasks.pipelines.flasksPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# DOWNLOADER_MIDDLEWARES = {
#     # ...
#     'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 100,
#     'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
#     'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
#     # ...
# }
# FEED_EXPORT_BATCH_ITEM_COUNT=10
ROTATING_PROXY_LIST_PATH = 'proxy.txt'
ROTATING_PROXY_PAGE_RETRY_TIMES=500
ROTATING_PROXY_BACKOFF_CAP=60
ROTATING_PROXY_BAN_POLICY = 'flasks.policy.BanPolicy'
DOWNLOAD_TIMEOUT=10

# ITEM_PIPELINES = {
#     'flasks.pipelines.CSVPipeline': 300,
# }

# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
# }
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'

# LOG_LEVEL = 'DEBUG'
# LOG_FILE = 'asdasd'
LOG_FILE_PATH = 'logs'
LOG_ENABLED = True
DATA_FILE_PATH = './outputs'
