import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin
from telegram import Bot
...
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
import random
import time

# List of real, recent User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def scrape_amazon():
    # Primary: Today's Deals page (goldbox)
    urls = [
        "https://www.amazon.in/gp/goldbox",
        "https://www.amazon.in/deals?ref_=nav_cs_gb",
    ]
    all_items = []
    session = requests.Session()
    for url in urls:
        try:
            # Random delay to appear human
            time.sleep(random.uniform(1, 3))
            r = session.get(url, headers=get_headers(), timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            # Try multiple possible selectors for deal cards
            items = (
                soup.select("div[data-testid='grid-deal']") or
                soup.select("div.DealGridItem-module__dealItem__3A6tE") or
                soup.select("div[data-testid='deal-card']") or
                soup.select("div.a-cardui-deal-card")
            )
            if items:
                for item in items:
                    title_el = (
                        item.select_one("span[data-testid='deal-title']") or
                        item.select_one("div[data-testid='deal-title']") or
                        item.select_one("span.a-size-base-plus")
                    )
                    link_el = (
                        item.select_one("a[data-testid='deal-link']") or
                        item.select_one("a.a-link-normal")
                    )
                    price_el = (
                        item.select_one("span[data-testid='deal-price']") or
                        item.select_one("span.a-price-whole")
                    )
                    if title_el and link_el:
                        title = title_el.text.strip()
                        link = link_el.get("href")
                        if link:
                            # sometimes link is relative
                            if not link.startswith("http"):
                                link = "https://www.amazon.in" + link
                            # Append affiliate tag
                            if "?" in link:
                                link += f"&tag={AMAZON_TAG}"
                            else:
                                link += f"?tag={AMAZON_TAG}"
                            price = price_el.text.strip() if price_el else "N/A"
                            all_items.append({"title": title, "price": price, "url": link, "platform": "Amazon"})
                if all_items:
                    break  # got deals, no need to try next URL
            else:
                print(f"No deal items found on {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return all_items

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
import json, os, random

DEALS_FILE = "deals_list.json"

def gather_all_deals():
    # Try loading from static file first (if exists)
    if os.path.exists(DEALS_FILE):
        with open(DEALS_FILE, "r") as f:
            static_deals = json.load(f)
        if static_deals:
            print(f"Using static deals: {len(static_deals)} available")
            return static_deals

    # Otherwise fallback to scraping (you may leave this empty for now)
    return []
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
