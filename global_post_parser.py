import re
import os
from datetime import datetime

# -------------------------
# CONFIGURATION
# -------------------------

INPUT_FILE = "global_post_articles.md"         # your long input file
OUTPUT_DIR = "portfolio/global_post"      # output folder for markdown files

DATE_PATTERN = r"(\d{1,2}/\d{1,2}/\d{2})"  # M/D/YY

# -------------------------
# HELPERS
# -------------------------

def normalize_date(date_str):
    """Convert M/D/YY → YYYY-MM-DD"""
    dt = datetime.strptime(date_str, "%m/%d/%y")
    return dt.strftime("%y/%m/%d")

def extract_country(line):
    """Extract the country name inside [COUNTRY](url) — preserving case from link text"""
    match = re.search(r"\[([A-Za-z0-9 \-]+)\]\(", line)
    if match:
        return match.group(1).strip().lower().replace(" ", "-")
    return "unknown"

# -------------------------
# PARSER
# -------------------------

def parse_articles(text):
    # Split on the date pattern but keep the date
    parts = re.split(DATE_PATTERN, text)
    parts = parts[1:]  # first element before first date is empty

    articles = []

    for i in range(0, len(parts), 2):
        date_str = parts[i].strip()
        body = parts[i + 1].strip()

        # Extract first lines: headline + country link + rest
        lines = body.split("\n", 3)

        headline = lines[0].strip() if len(lines) > 0 else ""
        country_line = lines[1].strip() if len(lines) > 1 else ""
        country_slug = extract_country(country_line)
        article_body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""

        # KEEP all markdown intact
        full_body = body

        articles.append({
            "date": date_str,
            "headline": headline,
            "country_slug": country_slug,
            "full_body": full_body
        })

    return articles

# -------------------------
# WRITER
# -------------------------

def write_markdown_files(articles):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for article in articles:
        date_norm = normalize_date(article["date"])
        slug = article["headline"].lower()
        slug = re.sub(r"[^\w\s-]", "", slug)   # remove punctuation
        slug = re.sub(r"\s+", "-", slug)       # spaces → single dash
        filename = f"{slug}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # File content — completely raw, ALL markdown preserved
        md = f"# {article['headline']}\n\n" \
             f"{date_norm}\n\n" \
             f"{article['full_body']}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"Created → {filepath}")

# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    articles = parse_articles(text)
    write_markdown_files(articles)

    print("✔ Done! Markdown files written, all links preserved.")
