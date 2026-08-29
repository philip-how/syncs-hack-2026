from telstra_payphone_scraper import fetch_all_payphones_near
results = fetch_all_payphones_near(-33.8688, 151.2093)  # Sydney CBD
print(len(results), "payphones found")
print(results[0] if results else "no results")