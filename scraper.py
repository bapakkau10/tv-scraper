import requests
from playwright.sync_api import sync_playwright

# Masukkan ID yang anda dapat tadi di sini
ACCOUNT_ID = "f136062d5216a667c849fce3f3feb4c6"
NAMESPACE_ID = "4f79afe4475c4d188bb9fc570e558c2b"
API_TOKEN = "cfut_6GdQu6KyO2iEo3A6XDcGhM8Rh6JtVrKtIW86nBdj5e815223"

def update_kv(m3u8_url):
    # API endpoint untuk update KV
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/live_m3u8"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    response = requests.put(url, data=m3u8_url, headers=headers)
    
    if response.status_code == 200:
        print("Berjaya update link ke KV!")
    else:
        print(f"Gagal update: {response.text}")

def get_m3u8_link():
    with sync_playwright() as p:
        # headless=True supaya tidak mengganggu skrin anda
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_request(request):
            # Cari link m3u8 yang ada token
            if ".m3u8" in request.url and "token=" in request.url:
                print(f"Jumpa link: {request.url}")
                update_kv(request.url)
                browser.close()

        page.on("request", handle_request)
        page.goto("https://malaysia-tv.net/tv3-live/")
        
        # Biarkan 15 saat untuk script load
        page.wait_for_timeout(15000)
        browser.close()

if __name__ == "__main__":
    get_m3u8_link()