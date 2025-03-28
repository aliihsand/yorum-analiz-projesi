import os
from datetime import datetime, timedelta
from google_play_scraper import reviews, Sort
from app.services.sentiment import analyze_sentiment
from dotenv import load_dotenv
import logging

load_dotenv()

BILETINIAL_PACKAGE = os.getenv("APP_PACKAGE")
THINKSUITE_PACKAGE = "com.dijitalsahne.thinkwork"
LANG = os.getenv("LANG", "tr")
COUNTRY = os.getenv("COUNTRY", "tr")

def fetch_reviews(months, app='biletinial'):
    if not BILETINIAL_PACKAGE:
        raise ValueError("APP_PACKAGE environment variable is not set")

    all_reviews = []
    continuation_token = None

    fetch_all = months == "all"
    try:
        limit_date = datetime.now() - timedelta(days=30 * int(months)) if not fetch_all else None
    except ValueError as e:
        raise ValueError(f"Invalid months value: {months}. Must be a number or 'all'") from e

    page_count = 0
    max_pages = 200  # güvenlik önlemi: 200 sayfaya kadar (20.000 yorum gibi)

    package = THINKSUITE_PACKAGE if app == 'thinksuite' else BILETINIAL_PACKAGE
    logging.info(f"Fetching reviews for package: {package}, months: {months}")

    try:
        while True:
            result, continuation_token = reviews(
                package,
                lang=LANG,
                country=COUNTRY,
                sort=Sort.NEWEST,
                count=100,    # 100 yorum çeker. Max
                continuation_token=continuation_token
            )

            for r in result:
                comment_date = r["at"]
                if not fetch_all and comment_date < limit_date:
                    return all_reviews

                all_reviews.append({
                    "comment": r["content"],
                    "rating": r["score"],
                    "sentiment": analyze_sentiment(r["content"]),
                    "date": comment_date.strftime("%Y-%m-%d")
                })

            page_count += 1
            if not continuation_token:
                break

            if page_count >= max_pages:
                break

        logging.info(f"Successfully fetched {len(all_reviews)} reviews")
        return all_reviews

    except Exception as e:
        logging.error(f"Error fetching reviews: {str(e)}")
        raise
