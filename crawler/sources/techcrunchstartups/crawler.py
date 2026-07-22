from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.techcrunchstartups import config
from crawler.sources.techcrunchstartups.parser import normalize_article_url, parse_article_page


class TechCrunchStartupsCrawler(RssFeedCrawler):
    """Crawls startup funding and company news from TechCrunch."""

    source_name = "techcrunchstartups"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "TechCrunch Startups"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
