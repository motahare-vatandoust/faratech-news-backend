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
    parser.add_argument(
        "--no-translate",
        action="store_true",
        help="Save crawled English text without GapGPT Farsi translation",
    )
    args = parser.parse_args()

    if args.save:
        from db.session import SessionLocal
        from services import crawler as crawler_service

        db = SessionLocal()
        try:
            translate = not args.no_translate
            result, saved_count = await crawler_service.run_crawl(
                db,
                args.source,
                limit=args.limit,
                persist=True,
                translate_to_farsi=translate,
            )
        finally:
            db.close()

        fetched = len(result.articles)
        skipped = len(result.skipped_urls)
        mode = "Farsi (GapGPT)" if translate else "English (no translation)"

        print(f"Source: {result.source}")
        print(f"Fetched from site: {fetched}")
        print(f"Saved to database: {saved_count}")
        print(f"Skipped (already exist): {skipped}")
        print(f"Translation: {mode}")

        if saved_count == 0 and skipped > 0 and not result.errors:
            print(
                "\nAll crawled articles are already in the news table. "
                "Try a higher --limit, or delete existing rows to re-import:\n"
                f"  DELETE FROM news WHERE source = '{result.source}';"
            )
        if result.skipped_urls:
            print("\nSkipped URLs:")
            for url in result.skipped_urls:
                print(f"  - {url}")
        if result.errors:
            print("\nErrors:")
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
