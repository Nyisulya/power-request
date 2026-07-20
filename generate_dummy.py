import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'power_request.settings')
django.setup()

from django.contrib.auth.models import User
from portal.models import Offering, CountryLeader

# Create superadmin (Pastor)
if not User.objects.filter(username='pastor').exists():
    User.objects.create_superuser('pastor', 'pastor@powerrequest.org', 'power2026')
    print("Created superadmin: pastor (password: power2026)")

# Create a country leader for Kenya
if not User.objects.filter(username='kenya_leader').exists():
    user_ke = User.objects.create_user('kenya_leader', 'kenya@powerrequest.org', 'power2026')
    CountryLeader.objects.create(user=user_ke, country='Kenya', phone_number='+254712345678')
    print("Created leader: kenya_leader (password: power2026)")

# Create a country leader for USA
if not User.objects.filter(username='usa_leader').exists():
    user_us = User.objects.create_user('usa_leader', 'usa@powerrequest.org', 'power2026')
    CountryLeader.objects.create(user=user_us, country='USA', phone_number='+15551234567')
    print("Created leader: usa_leader (password: power2026)")

# Create dummy offerings
countries = ['Tanzania', 'Kenya', 'USA', 'UK', 'Uganda']
methods = ['MPESA', 'BANK', 'CARD', 'PAYPAL']
currencies = {'Tanzania': 'TZS', 'Kenya': 'KES', 'USA': 'USD', 'UK': 'GBP', 'Uganda': 'UGX'}

if Offering.objects.count() < 10:
    for i in range(30):
        c = random.choice(countries)
        m = random.choice(methods)
        amt = random.randint(50, 500)
        
        # adjust amount for local currency
        if c in ['Tanzania', 'Uganda']:
            amt *= 1000
        elif c == 'Kenya':
            amt *= 100
            
        Offering.objects.create(
            donor_name=f"Faithful Partner {i+1}",
            amount=amt,
            currency=currencies[c],
            country=c,
            payment_method=m,
            transaction_id=f"TXN{random.randint(100000, 999999)}"
        )
    print("Created dummy offerings!")
else:
    print("Offerings already exist.")

print("Dummy data generated successfully!")
