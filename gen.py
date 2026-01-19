import json
import requests
import time
import re
import os

# --- TELEGRAM CONFIG ---
BOT_TOKEN = "8490318398:AAHGmTsiDuW8uBJuSXo_rzYDXbhN2ZvULbc"  # Replace with your bot token
CHAT_ID = "7243538468"      # Replace with your chat ID
# -----------------------

def send_to_telegram(message):
    if not BOT_TOKEN or not CHAT_ID or "YOUR" in BOT_TOKEN or "YOUR" in CHAT_ID:
        # Don't send if not configured
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending to Telegram: {str(e)}")

def load_cookies():
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies_list = json.load(f)

    return "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies_list)

def get_headers(cookie_string):
    return {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www.sheinindia.in",
        "pragma": "no-cache",
        "referer": "https://www.sheinindia.in/cart",
        "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "x-tenant-id": "SHEIN",
        "cookie": cookie_string
    }

def parse_vouchers_file():
    vouchers = []
    current_price = None
    
    with open("vouchers.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("=== PRICE"):
                price_match = re.search(r'₹(\d+)', line)
                if price_match:
                    current_price = price_match.group(1)
                continue

            if not line.startswith("==="):
                vouchers.append({
                    "code": line,
                    "price": current_price
                })
    return vouchers

def check_voucher(voucher_code, headers):
    url = "https://www.sheinindia.in/api/cart/apply-voucher"
    payload = {
        "voucherId": voucher_code,
        "device": {"client_type": "web"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.status_code, response.json()
    except Exception as e:
        print(f"Error checking voucher {voucher_code}: {str(e)}")
        return None, None

def reset_voucher(voucher_code, headers):
    url = "https://www.sheinindia.in/api/cart/reset-voucher"
    payload = {
        "voucherId": voucher_code,
        "device": {"client_type": "web"}
    }
    
    try:
        requests.post(url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        print(f"Error resetting voucher {voucher_code}: {str(e)}")

def is_voucher_applicable(response_data):
    if not response_data:
        return False

    if "errorMessage" in response_data:
        errors = response_data["errorMessage"].get("errors", [])
        for error in errors:
            if error.get("type") == "VoucherOperationError":
                if "not applicable" in error.get("message", "").lower():
                    return False

    return "errorMessage" not in response_data


def append_to_file(filename, price, code):
    
    
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"=== PRICE ₹{price} ===\n{code}\n")
        return

   
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    
    price_header = f"=== PRICE ₹{price} ==="
    if price_header not in content:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n{price_header}\n{code}\n")
    else:
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"{code}\n")

def main():
    print("Loading cookies...")
    cookie_string = load_cookies()
    headers = get_headers(cookie_string)

    print("Parsing vouchers...")
    vouchers = parse_vouchers_file()
    print(f"Found {len(vouchers)} vouchers to check\n")

    for i, voucher in enumerate(vouchers, 1):
        voucher_code = voucher["code"]
        price = voucher["price"]

        print(f"Checking voucher {i}/{len(vouchers)}: {voucher_code} (₹{price})")

        status_code, response_data = check_voucher(voucher_code, headers)

        if status_code is None:
            print("  Failed to check voucher\n")
            continue

        print(f"  Status: {status_code}")

        if is_voucher_applicable(response_data):
            print("  ✅ Applicable")
            append_to_file("applicable_vouchers.txt", price, voucher_code)
            message = f"✅ New valid voucher found!\n<b>Code:</b> {voucher_code}\n<b>Price:</b> ₹{price}"
            send_to_telegram(message)
        else:
            print("  ❌ Not applicable ")
            append_to_file("not_applicable_vouchers.txt", price, voucher_code)

        reset_voucher(voucher_code, headers)
        time.sleep(1)

    print("\n=== COMPLETED — Results saved live during the run ===")

if __name__ == "__main__":
    main()
