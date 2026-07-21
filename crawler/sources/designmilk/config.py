BASE_URL = "https://design-milk.com"
FEED_URL = f"{BASE_URL}/feed/"

ALLOWED_HOSTS = frozenset({"design-milk.com", "www.design-milk.com"})

EXCLUDED_SLUGS = frozenset(
    {
        "about",
        "advertise",
        "contact",
        "privacy-policy",
        "terms",
        "shop",
        "newsletter",
        "category",
        "tag",
        "author",
        "page",
        "feed",
    }
)
