from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

# Parameters that should NOT affect URL identity
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "phpsessid",
    "sessionid",
    "sid",
}


def normalize_url(url: str) -> str:
    """
    Normalize URLs so equivalent URLs become identical.
    """

    parsed = urlparse(url)

    # lowercase scheme and host
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # remove default ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]

    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # normalize path
    path = parsed.path

    # remove duplicate slashes
    while "//" in path:
        path = path.replace("//", "/")

    # remove trailing slash (except root)
    if path != "/":
        path = path.rstrip("/")

    # treat homepage and index pages as the same page
    if path in ("", "/", "/index.php", "/index.html"):
        path = ""

    # Remove tracking/session parameters but keep important ones
    query_items = [
    (k.lower(), v)
    for k, v in parse_qsl(parsed.query)
    if k.lower() not in TRACKING_PARAMS
    ]

    # Sort remaining parameters
    query = urlencode(sorted(query_items))

    return urlunparse((
        scheme,
        netloc,
        path,
        "",
        query,
        ""
    ))