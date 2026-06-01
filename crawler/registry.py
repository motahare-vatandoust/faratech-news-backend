from typing import Dict, Type

from crawler.base import BaseCrawler
from crawler.sources.deepmind.crawler import DeepMindCrawler
from crawler.sources.dzone.crawler import DZoneCrawler

_CRAWLERS: Dict[str, Type[BaseCrawler]] = {
    DZoneCrawler.source_name: DZoneCrawler,
    DeepMindCrawler.source_name: DeepMindCrawler,
}


def get_crawler(source: str) -> BaseCrawler:
    crawler_cls = _CRAWLERS.get(source)
    if crawler_cls is None:
        known = ", ".join(sorted(_CRAWLERS))
        raise ValueError(f"Unknown crawler source '{source}'. Known sources: {known}")
    return crawler_cls()


def list_sources() -> list[str]:
    return sorted(_CRAWLERS.keys())


def get_source_base_urls() -> dict[str, str]:
    return {name: cls.base_url for name, cls in _CRAWLERS.items()}
