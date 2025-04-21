# file that works with the UCSB menu API to get items, etc.

import os
import requests
from dotenv import load_dotenv, find_dotenv
from datetime import date
import time

load_dotenv(find_dotenv())

# 1) Configuration
API_BASE = "https://api.ucsb.edu/dining/menu/v1"
API_KEY  =  os.getenv("API_KEY")
print(API_KEY)

headers = {
    "ucsb-api-key": API_KEY
}

resp = requests.get(f"{API_BASE}/",       headers=headers)
resp.raise_for_status()
info = resp.json()
print("Daily menu:", info)

today = date.today().isoformat()
resp = requests.get(
    f"{API_BASE}/meals/names",
    headers=headers,
    params={"date": today}
)
resp.raise_for_status()
meals = resp.json()
print(f"Meals on {today}:", meals)

today = time.strftime("%Y-%m-%d", time.localtime())
resp = requests.get(f"{API_BASE}/hours/{today}", headers=headers)
resp.raise_for_status()
hours = resp.json()
print("Service Hours:", hours)
