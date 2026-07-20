import requests
from django.conf import settings
import uuid

class PesaPalAPI:
    def __init__(self):
        self.consumer_key = settings.PESAPAL_CONSUMER_KEY
        self.consumer_secret = settings.PESAPAL_CONSUMER_SECRET
        self.is_live = getattr(settings, 'PESAPAL_IS_LIVE', True)
        self.base_url = "https://pay.pesapal.com/v3/api" if self.is_live else "https://cybqa.pesapal.com/v3/api"
        
        self.token = None
        
    def get_auth_token(self):
        url = f"{self.base_url}/Auth/RequestToken"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            return self.token
        else:
            raise Exception(f"PesaPal Auth Failed: {response.text}")
            
    def register_ipn(self, ipn_url):
        if not self.token:
            self.get_auth_token()
            
        url = f"{self.base_url}/URLSetup/RegisterIPN"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        payload = {
            "url": ipn_url,
            "ipn_notification_type": "POST"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('ipn_id')
        else:
            raise Exception(f"PesaPal IPN Registration Failed: {response.text}")

    def submit_order(self, amount, currency, description, callback_url, ipn_id, first_name, email, phone):
        if not self.token:
            self.get_auth_token()
            
        merchant_reference = str(uuid.uuid4())
        
        url = f"{self.base_url}/Transactions/SubmitOrderRequest"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        payload = {
            "id": merchant_reference,
            "currency": currency,
            "amount": float(amount),
            "description": description,
            "callback_url": callback_url,
            "notification_id": ipn_id,
            "billing_address": {
                "email_address": email or "anonymous@powerrequest.org",
                "phone_number": phone or "",
                "country_code": "",
                "first_name": first_name or "Anonymous",
                "middle_name": "",
                "last_name": "",
                "line_1": "",
                "line_2": "",
                "city": "",
                "state": "",
                "postal_code": "",
                "zip_code": ""
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "order_tracking_id": data.get("order_tracking_id"),
                "merchant_reference": data.get("merchant_reference"),
                "redirect_url": data.get("redirect_url")
            }
        else:
            raise Exception(f"PesaPal Order Submit Failed: {response.text}")

    def get_transaction_status(self, order_tracking_id):
        if not self.token:
            self.get_auth_token()
            
        url = f"{self.base_url}/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"PesaPal Get Status Failed: {response.text}")
