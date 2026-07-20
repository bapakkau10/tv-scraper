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
        print(f"Update KV Status: {response.status_code}")
    except Exception as e:
        print(f"Error update: {e}")

def get_m3u8_link():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Guna context supaya lebih stabil
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()

        # Kita simpan semua link yang jumpa dalam list
        found_links = []

        def handle_request(request):
            if ".m3u8" in request.url:
                found_links.append(request.url)

        page.on("request", handle_request)
        
        try:
            print("Membuka laman web...")
            page.goto("https://malaysia-tv.net/tv3-live/", timeout=60000)
            page.wait_for_timeout(15000) # Tunggu 15 saat untuk video loaded
            
            # Logik Pemilihan: Cari link yang ada 1080p, kalau takde baru cari yang lain
            best_link = None
            for link in found_links:
                if "1080" in link or "fhd" in link.lower():
                    best_link = link
                    break # Dah jumpa 1080p, terus stop
            
            if not best_link and found_links:
                best_link = found_links[-1] # Ambil link terakhir kalau 1080p tak jumpa

            if best_link:
                print(f"Link terpilih (FHD jika ada): {best_link}")
                update_kv(best_link)
            else:
                print("Tiada link m3u8 dijumpai!")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_m3u8_link()
