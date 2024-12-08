# Web scraping is dissalowed will be changing this for something else later -.
#
#
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


# Create a session
session = requests.Session()

# Target URL
url = "https://www.aruodas.lt/butai/kaune/"

# Update headers with a real User-Agent
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.aruodas.lt/",
    "Connection": "keep-alive"
})

# Check if page is active
try:
    response = session.get(url, timeout=10)
    response.raise_for_status()  # Ensure the request succeeded
    soup = BeautifulSoup(response.text, "html.parser")  # Correct parser
    print("Page fetched successfully.")
    print(soup.prettify()[:500])  # Preview HTML

    # Extract listings
    listings = soup.select("div.list-row-v2")  # Correct CSS selector

    for listing in listings:
        try:
            # Extract price
            price = listing.select_one(".list-item-price-v2").text.strip() if listing.select_one(".list-item-price-v2") else "N/A"

            # Extract rooms
            rooms = listing.select_one(".list-RoomNum-v2").text.strip() if listing.select_one(".list-RoomNum-v2") else "N/A"

            # Extract area
            area = listing.select_one(".list-AreaOverall-v2").text.strip() if listing.select_one(".list-AreaOverall-v2") else "N/A"

            # Extract address
            address = listing.select_one(".list-address-v2").text.strip() if listing.select_one(".list-address-v2") else "N/A"

            print(f"Price: {price}")
            print(f"Rooms: {rooms}")
            print(f"Area: {area} m²")
            print(f"Address: {address}")
            print("-" * 50)

        except AttributeError:
            print("Missing data in this listing. Skipping...")
            continue
except requests.exceptions.RequestException as e:
    print(f"Failed fetching the page: {e}")

# Delay between requests to avoid blocking
time.sleep(10)
