from django.db import models

class SystemSetting(models.Model):
    google_meet_link = models.URLField(max_length=500, default="https://meet.google.com/")
    daily_verse_en = models.TextField(default="For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life. - John 3:16")
    daily_verse_sw = models.TextField(default="Kwa maana jinsi hii Mungu aliupenda ulimwengu, hata akamtoa Mwanawe pekee, ili kila mtu amwaminiye asipotee, bali awe na uzima wa milele. - Yohana 3:16")
    prayer_time_utc = models.DateTimeField(null=True, blank=True)
    
    # Offering/Giving Configurations
    mpesa_lipa_namba = models.CharField(max_length=50, default="552211", blank=True)
    tigopesa_lipa_namba = models.CharField(max_length=50, default="443322", blank=True)
    airtel_lipa_namba = models.CharField(max_length=50, default="112233", blank=True)
    bank_name = models.CharField(max_length=150, default="CRDB Bank", blank=True)
    bank_account_number = models.CharField(max_length=100, default="0152435467800", blank=True)
    bank_account_name = models.CharField(max_length=150, default="POWER REQUEST GROUP", blank=True)
    paypal_link = models.CharField(max_length=500, default="https://paypal.me/powerrequest", blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1  # Always overwrite the first row to ensure singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System Settings"

class PrayerRequest(models.Model):
    author_name = models.CharField(max_length=150)
    content_en = models.TextField(blank=True)
    content_sw = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_country = models.CharField(max_length=100, default="Unknown")

    def __str__(self):
        return f"Request by {self.author_name} ({self.user_country})"

class Testimony(models.Model):
    author_name = models.CharField(max_length=150)
    content_en = models.TextField(blank=True)
    content_sw = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_country = models.CharField(max_length=100, default="Unknown")

    def __str__(self):
        return f"Testimony by {self.author_name} ({self.user_country})"

class Announcement(models.Model):
    title_en = models.CharField(max_length=200)
    title_sw = models.CharField(max_length=200)
    content_en = models.TextField()
    content_sw = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_en

class LeaderProfile(models.Model):
    name = models.CharField(max_length=150)
    title_en = models.CharField(max_length=150)
    title_sw = models.CharField(max_length=150)
    bio_en = models.TextField()
    bio_sw = models.TextField()
    image = models.ImageField(upload_to='leaders/', blank=True, null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name
