"""
Scrapes public web pages listed in `SOURCE_URLS` and saves the extracted
paragraph text into a single file (default: academy.txt), used as the
knowledge source for app.py.

Run this BEFORE starting app.py, and re-run it whenever your source pages
change (e.g. you update your portfolio or LinkedIn summary).

Note on LinkedIn: LinkedIn blocks unauthenticated/automated requests for most
profile content and instead returns a login wall. This script does a basic
check for that and will warn you if it looks like a page wasn't scraped
properly, but it cannot bypass the login wall. If your LinkedIn data comes
back mostly empty, consider manually copying the relevant text from your
profile into the output file instead.
"""

import os
import sys

import requests
from bs4 import BeautifulSoup

SOURCE_URLS = [
    "https://my-portfolio-sandy-eight-15.vercel.app/",
    "https://www.linkedin.com/in/syed-mahmood-ejaz-a93910207",
]

OUTPUT_FILE = os.getenv("SCRAPE_OUTPUT_FILE", "academy.txt")

# A browser-like User-Agent improves the odds a site returns real content
# instead of a bot-blocking page. It does not bypass authentication walls.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

LOGIN_WALL_MARKERS = ["join now", "sign in", "authwall"]


def looks_like_login_wall(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in LOGIN_WALL_MARKERS)


def scrape(urls):
    all_text = ""

    for url in urls:
        print(f"Scraping: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException as error:
            print(f"  Failed to reach {url}: {error}")
            continue

        if response.status_code != 200:
            print(f"  Failed to retrieve {url}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        text = "\n".join(
            p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)
        )

        if not text:
            print(f"  Warning: no paragraph text extracted from {url}.")
        elif looks_like_login_wall(text):
            print(
                f"  Warning: {url} looks like it returned a login/auth wall "
                "instead of real content. This page likely needs manual copy-paste."
            )

        all_text += f"\n\n===== SOURCE: {url} =====\n\n{text}"
        print("  Done.")

    return all_text


def main():
    all_text = scrape(SOURCE_URLS)

    if not all_text.strip():
        print(
            "\nNo content was scraped from any source. "
            f"{OUTPUT_FILE} was not overwritten to avoid wiping existing data.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(all_text)

    print(f"\nAll website data saved successfully to {OUTPUT_FILE}!")


if __name__ == "__main__":
    main()
