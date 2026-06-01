BASE_URL = "https://deepmind.google"
BLOG_URL = f"{BASE_URL}/blog/"
ARTICLE_PATH_PREFIX = "/blog/"

# Only crawl posts hosted on deepmind.google/blog (skip e.g. antigravity.google links).
ALLOWED_HOSTS = frozenset({"deepmind.google", "www.deepmind.google"})
