import os
import requests
from playwright.sync_api import sync_playwright

ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
NAMESPACE_ID = os.environ.get("NAMESPACE_ID")
API_TOKEN = os.environ.get("API_TOKEN")


# =========================
# UPDATE CLOUDFLARE KV
# =========================
def update_kv(kv_key, m3u8_url):
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{ACCOUNT_ID}/storage/kv/namespaces/"
        f"{NAMESPACE_ID}/values/{kv_key}"
    )

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "text/plain"
    }

    response = requests.put(
        url,
        data=m3u8_url,
        headers=headers
    )

    if response.ok:
        print(f"[KV OK] {kv_key} updated")
    else:
        print(f"[KV ERROR] {kv_key}: {response.text}")


# =========================
# SCRAPE M3U8
# =========================
def get_m3u8_link(page, channel_name, page_url):

    print("\n==============================")
    print(f"SCRAPING: {channel_name}")
    print(f"URL: {page_url}")
    print("==============================")

    found_links = []

    def handle_request(request):
        if ".m3u8" in request.url:
            if request.url not in found_links:
                found_links.append(request.url)
                print(f"[M3U8 FOUND] {request.url}")

    page.on("request", handle_request)

    try:
        page.goto(
            page_url,
            timeout=60000,
            wait_until="domcontentloaded"
        )

        # Trigger player
        page.mouse.click(500, 500)

        # Tunggu player / stream load
        page.wait_for_timeout(20000)

        if found_links:

            # Kekalkan logic asal:
            # pilih URL paling panjang
            best_link = max(found_links, key=len)

            print(f"[SELECTED] {channel_name}")
            print(best_link)

            return best_link

        print(f"[FAILED] Tiada M3U8 untuk {channel_name}")
        return None

    except Exception as e:
        print(f"[ERROR] {channel_name}: {e}")
        return None

    finally:
        page.remove_listener("request", handle_request)


# =========================
# MAIN
# =========================
def main():

    channels = {

        # TV3 KEKALKAN KEY LAMA
        "TV3": {
            "url": "https://malaysia-tv.net/tv3-live/",
            "kv": "live_m3u8"
        },

        # TV8
        "TV8": {
            "url": "https://malaysia-tv.net/8-tv/",
            "kv": "tv8_m3u8"

         },

        # SiaraTV
        "SiaraTV": {
            "url": "https://tv3live.my/siara-tv/",
            "kv": "siaratv_m3u8"
            
        },

        # TV9
        "TV9": {
            "url": "https://malaysia-tv.net/tv9-malaysia/",
            "kv": "tv9_m3u8"
        }

    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={
                "width": 1920,
                "height": 1080
            }
        )

        page = context.new_page()

        for channel_name, config in channels.items():

            m3u8_url = get_m3u8_link(
                page,
                channel_name,
                config["url"]
            )

            if m3u8_url:

                update_kv(
                    config["kv"],
                    m3u8_url
                )

            else:
                print(
                    f"[SKIP] {channel_name} "
                    f"tidak update KV kerana M3U8 tidak dijumpai."
                )

        browser.close()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
