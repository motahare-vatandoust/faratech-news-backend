from typing import Dict, Type

from crawler.base import BaseCrawler
from crawler.sources.anthropic.crawler import AnthropicCrawler
from crawler.sources.bensbites.crawler import BensBitesCrawler
from crawler.sources.creativebloq.crawler import CreativeBloqCrawler
from crawler.sources.deepmind.crawler import DeepMindCrawler
from crawler.sources.designmilk.crawler import DesignMilkCrawler
from crawler.sources.dzone.crawler import DZoneCrawler
from crawler.sources.hubspot.crawler import HubSpotCrawler
from crawler.sources.huggingface.crawler import HuggingFaceCrawler
from crawler.sources.itsnicethat.crawler import ItsNiceThatCrawler
from crawler.sources.marketingweek.crawler import MarketingWeekCrawler
from crawler.sources.nngroup.crawler import NNGroupCrawler
from crawler.sources.rundown.crawler import RundownCrawler
from crawler.sources.smashingmagazine.crawler import SmashingMagazineCrawler
from crawler.sources.techcrunch.crawler import TechCrunchCrawler

_CRAWLERS: Dict[str, Type[BaseCrawler]] = {
    DZoneCrawler.source_name: DZoneCrawler,
    DeepMindCrawler.source_name: DeepMindCrawler,
    HubSpotCrawler.source_name: HubSpotCrawler,
    MarketingWeekCrawler.source_name: MarketingWeekCrawler,
    RundownCrawler.source_name: RundownCrawler,
    BensBitesCrawler.source_name: BensBitesCrawler,
    HuggingFaceCrawler.source_name: HuggingFaceCrawler,
    TechCrunchCrawler.source_name: TechCrunchCrawler,
    AnthropicCrawler.source_name: AnthropicCrawler,
    SmashingMagazineCrawler.source_name: SmashingMagazineCrawler,
    NNGroupCrawler.source_name: NNGroupCrawler,
    DesignMilkCrawler.source_name: DesignMilkCrawler,
    CreativeBloqCrawler.source_name: CreativeBloqCrawler,
    ItsNiceThatCrawler.source_name: ItsNiceThatCrawler,
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
