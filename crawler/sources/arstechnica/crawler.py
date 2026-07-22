from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.arstechnica import config
from crawler.sources.arstechnica.parser import normalize_article_url, parse_article_page


class ArsTechnicaCrawler(RssFeedCrawler):
    """Crawls hardware and gadgets coverage from Ars Technica."""

    source_name = "arstechnica"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "Ars Technica Gadgets"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
