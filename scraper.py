import os
import requests
from playwright.sync_api import sync_playwright

ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
NAMESPACE_ID = os.environ.get("NAMESPACE_ID")
API_TOKEN = os.environ.get("API_TOKEN")

def update_kv(m3u8_url):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/live_m3u8"
    headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "text/plain"}
    try:
        response = requests.put(url, data=m3u8_url, headers=headers)
        print(f"Update KV: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error update: {e}")

def get_m3u8_link():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()

        # DEBUG: Print SEMUA request yang keluar untuk kita tengok punca
        def handle_request(request):
            if ".m3u8" in request.url:
                print(f"DEBUG: Jumpa link .m3u8: {request.url}")
                update_kv(request.url)

        page.on("request", handle_request)
        
        try:
            print("Membuka laman web...")
            page.goto("https://malaysia-tv.net/tv3-live/", timeout=60000)
            page.wait_for_timeout(15000) # Tambah masa tunggu
            print("Selesai menunggu.")
        except Exception as e:
            print(f"Page load error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_m3u8_link()
