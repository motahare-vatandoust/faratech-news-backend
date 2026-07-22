from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.venturebeat import config
from crawler.sources.venturebeat.parser import normalize_article_url, parse_article_page


class VentureBeatCrawler(RssFeedCrawler):
    """Crawls startup and tech business news from VentureBeat."""

    source_name = "venturebeat"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "VentureBeat"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
