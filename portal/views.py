from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import SystemSetting, PrayerRequest, Testimony, Announcement, LeaderProfile, Follower
from .translator import translate_text

# A simple passcode for accessing the Leader Panel
LEADER_PASSCODE = "power2026"

def home(request):
    settings = SystemSetting.get_settings()
    prayer_time_iso = ""
    if settings.prayer_time_utc:
        prayer_time_iso = settings.prayer_time_utc.isoformat()

    prayer_requests = PrayerRequest.objects.all().order_by('-created_at')[:50]
    testimonies = Testimony.objects.all().order_by('-created_at')[:50]
    announcements = Announcement.objects.all().order_by('-created_at')[:10]

    context = {
        'settings': settings,
        'prayer_time_iso': prayer_time_iso,
        'prayer_requests': prayer_requests,
        'testimonies': testimonies,
        'announcements': announcements,
    }
    return render(request, 'portal/home.html', context)

def submit_request(request):
    if request.method == 'POST':
        author_name = request.POST.get('author_name', 'Anonymous').strip()
        content = request.POST.get('content', '').strip()
        user_country = request.POST.get('user_country', 'Global').strip()

        if not author_name:
            author_name = 'Anonymous'
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Content is required.'}, status=400)

        # Translate
        content_en, content_sw = translate_text(content)

        # Save
        prayer_request = PrayerRequest.objects.create(
            author_name=author_name,
            content_en=content_en,
            content_sw=content_sw,
            user_country=user_country
        )

        return JsonResponse({
            'success': True,
            'id': prayer_request.id,
            'author_name': prayer_request.author_name,
            'content_en': prayer_request.content_en,
            'content_sw': prayer_request.content_sw,
            'user_country': prayer_request.user_country,
            'created_at': prayer_request.created_at.isoformat()
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def submit_testimony(request):
    if request.method == 'POST':
        author_name = request.POST.get('author_name', 'Anonymous').strip()
        content = request.POST.get('content', '').strip()
        user_country = request.POST.get('user_country', 'Global').strip()

        if not author_name:
            author_name = 'Anonymous'

        if not content:
            return JsonResponse({'success': False, 'error': 'Content is required.'}, status=400)

        # Translate
        content_en, content_sw = translate_text(content)

        # Save
        testimony = Testimony.objects.create(
            author_name=author_name,
            content_en=content_en,
            content_sw=content_sw,
            user_country=user_country
        )

        return JsonResponse({
            'success': True,
            'id': testimony.id,
            'author_name': testimony.author_name,
            'content_en': testimony.content_en,
            'content_sw': testimony.content_sw,
            'user_country': testimony.user_country,
            'created_at': testimony.created_at.isoformat()
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def submit_registration(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        country = request.POST.get('country', 'Global').strip()

        if not full_name:
            return JsonResponse({'success': False, 'error': 'Name is required.'}, status=400)

        Follower.objects.create(
            full_name=full_name,
            email=email if email else None,
            phone_number=phone_number if phone_number else None,
            country=country if country else "Global"
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def leader_panel(request):
    # Check session
    is_leader = request.session.get('is_leader', False)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            passcode = request.POST.get('passcode', '').strip()
            if passcode == LEADER_PASSCODE:
                request.session['is_leader'] = True
                return redirect('leader_panel')
            else:
                return render(request, 'portal/leader.html', {
                    'error': 'Nenosiri si sahihi! / Incorrect passcode!',
                    'is_leader': False
                })

        elif action == 'logout':
            request.session['is_leader'] = False
            return redirect('leader_panel')

        # Actions requiring authentication
        if not is_leader:
            return redirect('leader_panel')

        if action == 'update_settings':
            google_meet_link = request.POST.get('google_meet_link', '').strip()
            daily_verse_en = request.POST.get('daily_verse_en', '').strip()
            daily_verse_sw = request.POST.get('daily_verse_sw', '').strip()
            prayer_time_raw = request.POST.get('prayer_time_utc', '').strip()

            settings = SystemSetting.get_settings()
            if google_meet_link:
                settings.google_meet_link = google_meet_link
            if daily_verse_en:
                settings.daily_verse_en = daily_verse_en
            if daily_verse_sw:
                settings.daily_verse_sw = daily_verse_sw
            
            if prayer_time_raw:
                parsed_dt = parse_datetime(prayer_time_raw)
                if parsed_dt:
                    if timezone.is_naive(parsed_dt):
                        parsed_dt = timezone.make_aware(parsed_dt, timezone.utc)
                    settings.prayer_time_utc = parsed_dt
            
            settings.save()
            return redirect('leader_panel')

        elif action == 'update_giving_settings':
            settings = SystemSetting.get_settings()
            settings.mpesa_lipa_namba = request.POST.get('mpesa_lipa_namba', '').strip()
            settings.tigopesa_lipa_namba = request.POST.get('tigopesa_lipa_namba', '').strip()
            settings.airtel_lipa_namba = request.POST.get('airtel_lipa_namba', '').strip()
            settings.bank_name = request.POST.get('bank_name', '').strip()
            settings.bank_account_number = request.POST.get('bank_account_number', '').strip()
            settings.bank_account_name = request.POST.get('bank_account_name', '').strip()
            settings.paypal_link = request.POST.get('paypal_link', '').strip()
            settings.save()
            return redirect('leader_panel')

        elif action == 'create_announcement':
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            
            if title and content:
                # Automate English and Swahili translations if only one translation is provided
                title_en, title_sw = translate_text(title)
                content_en, content_sw = translate_text(content)

                Announcement.objects.create(
                    title_en=title_en,
                    title_sw=title_sw,
                    content_en=content_en,
                    content_sw=content_sw
                )
            return redirect('leader_panel')

        elif action == 'create_leader':
            name = request.POST.get('name', '').strip()
            title = request.POST.get('title', '').strip()
            bio = request.POST.get('bio', '').strip()
            image = request.FILES.get('image')
            try:
                order = int(request.POST.get('order', '0'))
            except ValueError:
                order = 0

            if name and title and bio:
                title_en, title_sw = translate_text(title)
                bio_en, bio_sw = translate_text(bio)

                LeaderProfile.objects.create(
                    name=name,
                    title_en=title_en,
                    title_sw=title_sw,
                    bio_en=bio_en,
                    bio_sw=bio_sw,
                    image=image,
                    order=order
                )
            return redirect('leader_panel')

        elif action == 'delete_leader':
            leader_id = request.POST.get('id')
            if leader_id:
                profile = LeaderProfile.objects.filter(id=leader_id).first()
                if profile:
                    if profile.image:
                        profile.image.delete(save=False)
                    profile.delete()
                return JsonResponse({'success': True})

        elif action == 'delete_announcement':
            ann_id = request.POST.get('id')
            if ann_id:
                Announcement.objects.filter(id=ann_id).delete()
            return JsonResponse({'success': True})

        elif action == 'delete_request':
            request_id = request.POST.get('id')
            if request_id:
                PrayerRequest.objects.filter(id=request_id).delete()
            return JsonResponse({'success': True})

        elif action == 'delete_testimony':
            testimony_id = request.POST.get('id')
            if testimony_id:
                Testimony.objects.filter(id=testimony_id).delete()
            return JsonResponse({'success': True})

        elif action == 'delete_follower':
            follower_id = request.POST.get('id')
            if follower_id:
                Follower.objects.filter(id=follower_id).delete()
            return JsonResponse({'success': True})

    # GET requests
    if not is_leader:
        return render(request, 'portal/leader.html', {'is_leader': False})

    settings = SystemSetting.get_settings()
    prayer_time_iso = ""
    if settings.prayer_time_utc:
        prayer_time_iso = settings.prayer_time_utc.isoformat()

    prayer_requests = PrayerRequest.objects.all().order_by('-created_at')
    testimonies = Testimony.objects.all().order_by('-created_at')
    announcements = Announcement.objects.all().order_by('-created_at')
    leaders = LeaderProfile.objects.all().order_by('order')
    followers = Follower.objects.all().order_by('-created_at')

    context = {
        'is_leader': True,
        'settings': settings,
        'prayer_time_iso': prayer_time_iso,
        'prayer_requests': prayer_requests,
        'testimonies': testimonies,
        'announcements': announcements,
        'leaders': leaders,
        'followers': followers,
    }
    return render(request, 'portal/leader.html', context)

def about(request):
    settings = SystemSetting.get_settings()
    leaders = LeaderProfile.objects.all().order_by('order')
    return render(request, 'portal/about.html', {
        'settings': settings,
        'leaders': leaders
    })

def requests_room(request):
    settings = SystemSetting.get_settings()
    prayer_requests = PrayerRequest.objects.all().order_by('-created_at')
    context = {
        'settings': settings,
        'prayer_requests': prayer_requests,
    }
    return render(request, 'portal/requests_room.html', context)

def testimonies_room(request):
    settings = SystemSetting.get_settings()
    testimonies = Testimony.objects.all().order_by('-created_at')
    context = {
        'settings': settings,
        'testimonies': testimonies,
    }
    return render(request, 'portal/testimonies_room.html', context)

def giving(request):
    settings = SystemSetting.get_settings()
    return render(request, 'portal/giving.html', {'settings': settings})
