from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.krebsonsecurity import config
from crawler.sources.krebsonsecurity.parser import normalize_article_url, parse_article_page


class KrebsOnSecurityCrawler(RssFeedCrawler):
    """Crawls cybersecurity investigations from Krebs on Security."""

    source_name = "krebsonsecurity"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "Krebs on Security"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
