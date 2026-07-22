from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.thenewstack import config
from crawler.sources.thenewstack.parser import normalize_article_url, parse_article_page


class TheNewStackCrawler(RssFeedCrawler):
    """Crawls cloud and software engineering news from The New Stack."""

    source_name = "thenewstack"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "The New Stack"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
