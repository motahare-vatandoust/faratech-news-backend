"""CLI entrypoint: python -m crawler --source dzone --limit 5"""

import argparse
import asyncio
import json

from crawler.registry import get_crawler, list_sources


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Run a news source crawler")
    parser.add_argument(
        "--source",
        default="dzone",
        choices=list_sources(),
        help="Crawler source name",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum articles to fetch",
    )
    parser.add_argument(
        "--output",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save new articles to the news table (requires DATABASE_URL)",
    )
    args = parser.parse_args()

    if args.save:
        from db.session import SessionLocal
        from services import crawler as crawler_service

        db = SessionLocal()
        try:
            result, saved_count = await crawler_service.run_crawl(
                db, args.source, limit=args.limit, persist=True
            )
        finally:
            db.close()

        print(f"Source: {result.source}")
        print(f"Saved: {saved_count}, skipped: {len(result.skipped_urls)}")
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")
        return

    crawler = get_crawler(args.source)
    result = await crawler.crawl(limit=args.limit)

    if args.output == "json":
        print(result.model_dump_json(indent=2))
        return

    print(f"Source: {result.source}")
    print(f"Articles: {len(result.articles)}")
    for article in result.articles:
        print(f"  - {article.title} ({article.source_url})")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(_main())
