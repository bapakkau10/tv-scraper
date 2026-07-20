import os
import requests
from playwright.sync_api import sync_playwright

ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
NAMESPACE_ID = os.environ.get("NAMESPACE_ID")
API_TOKEN = os.environ.get("API_TOKEN")

def update_kv(m3u8_url):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/live_m3u8"
    headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "text/plain"}
    requests.put(url, data=m3u8_url, headers=headers)

def get_m3u8_link():
    with sync_playwright() as p:
        # Launch dengan arguments tambahan untuk meniru browser sebenar
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        found_links = []
        def handle_request(request):
            if ".m3u8" in request.url:
                found_links.append(request.url)

        page.on("request", handle_request)
        
        try:
            # Buka page dan paksa scroll sedikit untuk trigger video player
            page.goto("https://malaysia-tv.net/tv3-live/", timeout=60000)
            page.mouse.click(500, 500) 
            page.wait_for_timeout(20000) 
            
            # Cari link yang paling panjang/kompleks (biasanya master playlist lebih panjang)
            # atau cari yang tiada token
            best_link = max(found_links, key=len) if found_links else None
            
            if best_link:
                print(f"Link terpilih: {best_link}")
                update_kv(best_link)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_m3u8_link()
