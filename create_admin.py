import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "power_request.settings")
django.setup()

from django.contrib.auth.models import User
from portal.models import CountryLeader

# Badilisha hizi taarifa kama unavyopenda
USERNAME = "nyisuadmin"
EMAIL = "admin@nyisu.com"
PASSWORD = "PowerPassword2026!"

def create_superadmin():
    if not User.objects.filter(username=USERNAME).exists():
        print(f"[*] Natengeneza akaunti ya Superadmin: {USERNAME}...")
        user = User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
        print("[+] Akaunti imetengenezwa kikamilifu!")
        
        # Pia tunamfanya awe CountryLeader wa "Dunia Nzima" (Global)
        CountryLeader.objects.get_or_create(
            user=user,
            defaults={'country': 'Dunia Nzima (Global)', 'phone_number': '+255000000000'}
        )
        print("[+] Profile ya uongozi imeunganishwa vizuri!")
    else:
        print(f"[-] Akaunti yenye jina '{USERNAME}' tayari ipo kwenye mfumo.")
        user = User.objects.get(username=USERNAME)
        user.set_password(PASSWORD)
        user.save()
        print(f"[+] Password imesasishwa (Updated) kuwa mpya kwa usalama!")

if __name__ == "__main__":
    create_superadmin()
    print("\n=========================================")
    print("INGIA KWENYE DASHBOARD KWA KUTUMIA:")
    print(f"Username: {USERNAME}")
    print(f"Password: {PASSWORD}")
    print("=========================================\n")
