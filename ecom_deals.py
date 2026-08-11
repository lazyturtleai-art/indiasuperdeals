import requests
from bs4 import BeautifulSoup
import random, json, os, time, threading
from urllib.parse import urljoin

# ===================== CONFIGURATION =====================
TELEGRAM_TOKEN = "8610741436:AAHRfEQE7VggV5SSYlncvBhOIILDPfUIqB4"          # from BotFather
CHANNEL_ID = "@indiasupereals"        # e.g., @IndiaSuperDeals
AMAZON_TAG = "mukesh0bd7-21"                 # Amazon Associates tag
CUELINKS_API_KEY = "placeholder"           # will update after approval
# ==========================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DEALS_FILE = "deals_list.json"

# ---------- Static deals fallback ----------
def gather_all_deals():
    if os.path.exists(DEALS_FILE):
        with open(DEALS_FILE, "r") as f:
            static_deals = json.load(f)
        if static_deals:
            print(f"Using static deals: {len(static_deals)} available")
            return static_deals
    return []

# ---------- Formatting ----------
def format_post(deal):
    emoji = random.choice(["🔥", "⚡", "💥", "🛍️", "🚀"])
    return (
        f"{emoji} {deal['title']}\n"
        f"💰 {deal['price']}\n"
        f"🔗 {deal['url']}\n"
        f"🏷️ {deal['platform']} | @IndiaSuperDeals"
    )

# ---------- Posting via raw HTTP ----------
def post_random_deal():
    deals = gather_all_deals()
    if not deals:
        print("No deals found this hour.")
        return
    deal = random.choice(deals)
    msg = format_post(deal)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": msg,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Posted: {deal['title']}")
    except Exception as e:
        print(f"Post error: {e}")

if __name__ == "__main__":
    post_random_deal()
