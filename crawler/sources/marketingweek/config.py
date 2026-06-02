BASE_URL = "https://www.marketingweek.com"
HOME_URL = f"{BASE_URL}/"

ALLOWED_HOSTS = frozenset({"www.marketingweek.com", "marketingweek.com"})

# Exclude section/index pages and utility routes.
EXCLUDED_FIRST_SEGMENTS = frozenset(
    {
        "category",
        "tag",
        "author",
        "topic",
        "events",
        "podcasts",
        "jobs",
        "about",
        "contact",
        "newsletters",
        "search",
        "wp-content",
        "cdn-cgi",
    }
)
