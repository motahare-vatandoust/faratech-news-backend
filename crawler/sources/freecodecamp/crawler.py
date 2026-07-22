from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.freecodecamp import config
from crawler.sources.freecodecamp.parser import normalize_article_url, parse_article_page


class FreeCodeCampCrawler(RssFeedCrawler):
    """Crawls programming tutorials and news from freeCodeCamp."""

    source_name = "freecodecamp"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "freeCodeCamp"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
