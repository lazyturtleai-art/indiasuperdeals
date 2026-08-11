import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin
from telegram import Bot

# ===================== CONFIGURATION =====================
TELEGRAM_TOKEN = "8610741436:AAHRfEQE7VggV5SSYlncvBhOIILDPfUIqB4"          # from BotFather
CHANNEL_ID = "@indiasuperdeals"        # e.g., @IndiaSuperDeals
AMAZON_TAG = "mukesh0bd7-21"                 # Amazon Associates tag
CUELINKS_API_KEY = "placeholder"           # will be updated after approval
# ==========================================================

bot = Bot(token=TELEGRAM_TOKEN)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def cuelinks_affiliate(original_url):
    """Convert any store URL to affiliate link via Cuelinks (not used while pending)."""
    try:
        resp = requests.get(
            "https://api.cuelinks.com/v2/deep-link",
            headers={"X-Api-Key": CUELINKS_API_KEY},
            params={"url": original_url, "campaign_name": "telegram_deals"},
            timeout=10
        )
        data = resp.json()
        if data.get("success"):
            return data["data"]["affiliate_link"]
    except Exception as e:
        print(f"Cuelinks error: {e}")
    return original_url

# ---------- SCRAPERS ----------
def scrape_amazon():
    url = "https://www.amazon.in/gp/goldbox"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("div[data-testid='grid-deal']")
    deals = []
    for item in items:
        title_el = item.select_one("span[data-testid='deal-title']")
        link_el = item.select_one("a[data-testid='deal-link']")
        price_el = item.select_one("span[data-testid='deal-price']")
        if title_el and link_el:
            title = title_el.text.strip()
            link = urljoin("https://www.amazon.in", link_el["href"])
            # Add Amazon tag
            if "?" in link:
                link += f"&tag={AMAZON_TAG}"
            else:
                link += f"?tag={AMAZON_TAG}"
            price = price_el.text.strip() if price_el else "N/A"
            deals.append({"title": title, "price": price, "url": link, "platform": "Amazon"})
    return deals

def scrape_flipkart():
    url = "https://www.flipkart.com/offers-store"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.select("a._31qSD5")
    deals = []
    for card in cards:
        title_el = card.select_one("div._3wU53n") or card.select_one("a.IRpwTa")
        price_el = card.select_one("div._30jeq3")
        if title_el and card.get("href"):
            title = title_el.text.strip()
            link = urljoin("https://www.flipkart.com", card["href"])
            affiliate_link = cuelinks_affiliate(link)
            price = price_el.text.strip() if price_el else "N/A"
            deals.append({"title": title, "price": price, "url": affiliate_link, "platform": "Flipkart"})
    return deals

def scrape_shopsy():
    url = "https://www.shopsy.in/offers"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a[href*='/product/']")
    deals = []
    for link in links[:10]:
        title = link.get("title") or link.text.strip()
        href = urljoin("https://www.shopsy.in", link["href"])
        affiliate = cuelinks_affiliate(href)
        if title:
            deals.append({"title": title, "price": "Check price", "url": affiliate, "platform": "Shopsy"})
    return deals

def scrape_ajio():
    url = "https://www.ajio.com/sale"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("div.item") or soup.select("a[href*='/p/']")
    deals = []
    for item in items:
        name_el = item.select_one(".name") or item.select_one("div.brand")
        price_el = item.select_one(".price") or item.select_one("span.price")
        link_el = item if item.name == "a" else item.select_one("a")
        if name_el and link_el:
            title = name_el.text.strip()
            href = urljoin("https://www.ajio.com", link_el.get("href"))
            affiliate = cuelinks_affiliate(href)
            price = price_el.text.strip() if price_el else "N/A"
            deals.append({"title": title, "price": price, "url": affiliate, "platform": "AJIO"})
    return deals

def scrape_myntra():
    url = "https://www.myntra.com/sale"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.select("li.product-base")
    deals = []
    for card in cards:
        link = card.select_one("a")
        brand = card.select_one(".product-brand")
        price = card.select_one(".product-discountedPrice")
        if link and brand:
            title = brand.text.strip()
            href = urljoin("https://www.myntra.com", link["href"])
            affiliate = cuelinks_affiliate(href)
            price_text = price.text.strip() if price else "N/A"
            deals.append({"title": title, "price": price_text, "url": affiliate, "platform": "Myntra"})
    return deals

def scrape_bigbasket():
    url = "https://www.bigbasket.com/offers/"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.select("div.product-card") or soup.select("a[href*='/pd/']")
    deals = []
    for card in cards[:10]:
        title_el = card.select_one("h3") or card.select_one("div.prod-name")
        price_el = card.select_one("span.discnt-price") or card.select_one("span.price")
        link_el = card if card.name == "a" else card.select_one("a")
        if title_el and link_el:
            title = title_el.text.strip()
            href = urljoin("https://www.bigbasket.com", link_el.get("href"))
            affiliate = cuelinks_affiliate(href)
            price = price_el.text.strip() if price_el else "N/A"
            deals.append({"title": title, "price": price, "url": affiliate, "platform": "BigBasket"})
    return deals

# ---------- MAIN ENGINE ----------
def gather_all_deals():
    all_deals = []
    # TEMPORARY: Only Amazon while Cuelinks is pending approval
    scrapers = [
        ("Amazon", scrape_amazon),
        # ("Flipkart", scrape_flipkart),
        # ("Shopsy", scrape_shopsy),
        # ("AJIO", scrape_ajio),
        # ("Myntra", scrape_myntra),
        # ("BigBasket", scrape_bigbasket),
    ]
    for name, func in scrapers:
        try:
            deals = func()
            print(f"{name}: {len(deals)} deals")
            all_deals.extend(deals)
        except Exception as e:
            print(f"{name} scrape failed: {e}")
    return all_deals

def format_post(deal):
    emoji = random.choice(["🔥", "⚡", "💥", "🛍️", "🚀"])
    return (
        f"{emoji} {deal['title']}\n"
        f"💰 {deal['price']}\n"
        f"🔗 {deal['url']}\n"
        f"🏷️ {deal['platform']} | @IndiaSuperDeals"
    )

def post_random_deal():
    deals = gather_all_deals()
    if not deals:
        print("No deals found this hour.")
        return
    deal = random.choice(deals)
    msg = format_post(deal)
    try:
        bot.send_message(chat_id=CHANNEL_ID, text=msg, disable_web_page_preview=True)
        print(f"Posted: {deal['title']}")
    except Exception as e:
        print(f"Post error: {e}")

if __name__ == "__main__":
    post_random_deal()
