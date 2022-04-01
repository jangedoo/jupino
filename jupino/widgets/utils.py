import urllib.request


def open_image(path_or_url: str):
    if path_or_url.lower().startswith("http"):
        with urllib.request.urlopen(path_or_url) as f:
            return f.read()
    else:
        with open(path_or_url, "rb") as f:
            return f.read()
