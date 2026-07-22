from crawler.rss_crawler import RssFeedCrawler
from crawler.sources.thehackernews import config
from crawler.sources.thehackernews.parser import normalize_article_url, parse_article_page


class TheHackerNewsCrawler(RssFeedCrawler):
    """Crawls cybersecurity news from The Hacker News."""

    source_name = "thehackernews"
    base_url = config.BASE_URL
    feed_url = config.FEED_URL
    feed_label = "The Hacker News"
    normalize_url = staticmethod(normalize_article_url)
    parse_article = staticmethod(parse_article_page)
