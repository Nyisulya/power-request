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
    pesapal_ipn_id = models.CharField(max_length=100, blank=True, null=True)

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

class Follower(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male (Mwanaume)'),
        ('F', 'Female (Mwanamke)'),
        ('O', 'Other (Nyingine)'),
    ]
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, default="Global", blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

# --- Daily Quiz Feature Models ---

class DailyQuestion(models.Model):
    question_text_en = models.CharField(max_length=500)
    question_text_sw = models.CharField(max_length=500)
    
    option_a_en = models.CharField(max_length=200, default="-")
    option_a_sw = models.CharField(max_length=200, default="-")
    option_b_en = models.CharField(max_length=200, default="-")
    option_b_sw = models.CharField(max_length=200, default="-")
    option_c_en = models.CharField(max_length=200, default="-")
    option_c_sw = models.CharField(max_length=200, default="-")
    option_d_en = models.CharField(max_length=200, default="-")
    option_d_sw = models.CharField(max_length=200, default="-")
    
    OPTION_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES, default='A')
    
    active_date = models.DateField(help_text="The date this question is shown")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question for {self.active_date}"

class DailyQuizSession(models.Model):
    follower = models.ForeignKey(Follower, on_delete=models.CASCADE)
    active_date = models.DateField()
    start_time = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.FloatField(default=0.0)
    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('follower', 'active_date')

class ParticipantAnswer(models.Model):
    follower = models.ForeignKey(Follower, on_delete=models.CASCADE)
    question = models.ForeignKey(DailyQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, default='A')
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('follower', 'question')

    def __str__(self):
        return f"{self.follower.full_name} - {'Correct' if self.is_correct else 'Wrong'}"

# --- CRM & Management Models ---

from django.contrib.auth.models import User

class CountryLeader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="leader_profile")
    country = models.CharField(max_length=100, help_text="Country this leader manages (e.g. Kenya, USA)")
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.country}"

class Offering(models.Model):
    PAYMENT_METHODS = [
        ('MPESA', 'M-Pesa'),
        ('TIGOPESA', 'Tigo Pesa'),
        ('AIRTEL', 'Airtel Money'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit/Debit Card (Flutterwave/Stripe)'),
        ('PAYPAL', 'PayPal'),
        ('PESAPAL', 'PesaPal (Mobile/Card)'),
        ('OTHER', 'Other'),
    ]
    
    donor_name = models.CharField(max_length=200, blank=True, null=True, default="Anonymous")
    donor_email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="TZS")
    country = models.CharField(max_length=100, default="Tanzania", help_text="Country where the offering came from")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='OTHER')
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    merchant_reference = models.CharField(max_length=200, unique=True, blank=True, null=True)
    order_tracking_id = models.CharField(max_length=200, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_received = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} {self.currency} from {self.donor_name} ({self.country})"
