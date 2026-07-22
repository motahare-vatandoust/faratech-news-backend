from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.tomshardware import config
from crawler.sources.tomshardware.parser import normalize_article_url, parse_article_page


class TomsHardwareCrawler(RssFeedCrawler):
    """Crawls PC hardware and component news from Tom's Hardware."""

    source_name = "tomshardware"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "Tom's Hardware"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
