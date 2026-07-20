from django.contrib import admin
from .models import (
    SystemSetting, PrayerRequest, Testimony, Announcement, 
    LeaderProfile, Follower, DailyQuestion, DailyQuizSession, 
    ParticipantAnswer, CountryLeader, Offering,
    SermonSeries, SermonLesson
)

admin.site.register(SystemSetting)
admin.site.register(PrayerRequest)
admin.site.register(Testimony)
admin.site.register(Announcement)
admin.site.register(LeaderProfile)
admin.site.register(Follower)
admin.site.register(DailyQuestion)
admin.site.register(DailyQuizSession)
admin.site.register(ParticipantAnswer)
admin.site.register(CountryLeader)

@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'amount', 'currency', 'country', 'payment_method', 'date_received')
    list_filter = ('country', 'payment_method', 'currency', 'is_verified')
    search_fields = ('donor_name', 'donor_email', 'transaction_id', 'country')

admin.site.register(SermonSeries)
admin.site.register(SermonLesson)
