BASE_URL = "https://dzone.com"
HOME_URL = f"{BASE_URL}/"

# Editorial / meta pages linked from the homepage, not news articles.
EXCLUDED_ARTICLE_SLUGS = frozenset(
    {
        "how-to-submit-a-post-to-dzone",
        "dzones-article-submission-guidelines",
    }
)

ARTICLE_PATH_PREFIX = "/articles/"
