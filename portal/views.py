from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Count, Avg
from .models import SystemSetting, PrayerRequest, Testimony, Announcement, LeaderProfile, Follower, DailyQuestion, DailyQuizSession, ParticipantAnswer
from .translator import translate_text

# A simple passcode for accessing the Leader Panel
LEADER_PASSCODE = "power2026"

def home(request):
    settings = SystemSetting.get_settings()
    prayer_time_iso = ""
    if settings.prayer_time_utc:
        prayer_time_iso = settings.prayer_time_utc.isoformat()

    prayer_requests = PrayerRequest.objects.all().order_by('-created_at')[:5]
    testimonies = Testimony.objects.all().order_by('-created_at')[:5]
    announcements = Announcement.objects.all().order_by('-created_at')[:10]

    today = timezone.localdate()
    today_questions = DailyQuestion.objects.filter(active_date=today).order_by('id')
    daily_top_5 = []
    if today_questions.exists():
        daily_top_5 = DailyQuizSession.objects.filter(
            active_date=today, is_completed=True, score__gt=0
        ).select_related('follower').order_by('-score', 'time_taken_seconds')[:5]

    context = {
        'settings': settings,
        'prayer_time_iso': prayer_time_iso,
        'prayer_requests': prayer_requests,
        'testimonies': testimonies,
        'announcements': announcements,
        'daily_top_5': daily_top_5,
        'today_questions': today_questions,
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
        gender = request.POST.get('gender', 'M').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        country = request.POST.get('country', 'Global').strip()

        if not full_name:
            return JsonResponse({'success': False, 'error': 'Name is required.'}, status=400)

        # Prevent duplicates
        follower = None
        if phone_number:
            follower = Follower.objects.filter(phone_number=phone_number).first()
        
        if not follower:
            # Try to match by exact name and country if no phone
            follower = Follower.objects.filter(full_name__iexact=full_name, country__iexact=country).first()
            
        if follower:
            # Update info if they exist
            follower.full_name = full_name
            if country and country != 'Global':
                follower.country = country
            if phone_number:
                follower.phone_number = phone_number
            follower.save()
        else:
            follower = Follower.objects.create(
                full_name=full_name,
                gender=gender,
                phone_number=phone_number if phone_number else None,
                country=country if country else "Global"
            )
        return JsonResponse({
            'success': True,
            'full_name': follower.full_name,
            'country': follower.country,
            'identifier': follower.phone_number or f"ID-{follower.id}"
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def leader_panel(request):
    return redirect('dashboard')

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

def get_daily_question(request):
    today = timezone.localdate()
    question = DailyQuestion.objects.filter(active_date=today).first()
    if not question:
        return JsonResponse({'success': False, 'error': 'Hakuna swali la leo / No question for today'})
    
    return JsonResponse({
        'success': True,
        'id': question.id,
        'text_en': question.question_text_en,
        'text_sw': question.question_text_sw
    })

def start_quiz_session(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        
        if identifier.startswith('ID-'):
            try:
                fid = int(identifier.replace('ID-', ''))
                follower = Follower.objects.filter(id=fid).first()
            except ValueError:
                follower = None
        else:
            follower = Follower.objects.filter(email=identifier).first() or Follower.objects.filter(phone_number=identifier).first()
            
        if not follower:
            return JsonResponse({'success': False, 'error': 'Hujasajiliwa! Tafadhali jiunge na familia (Join Family) kwanza / Please join family first'})
        
        today = timezone.localdate()
        today_questions = DailyQuestion.objects.filter(active_date=today)
        if not today_questions.exists():
            return JsonResponse({'success': False, 'error': 'Hakuna swali leo / No questions for today'})
            
        session, created = DailyQuizSession.objects.get_or_create(follower=follower, active_date=today)
        if session.is_completed:
             return JsonResponse({'success': False, 'error': 'Umeshafanya swali la leo / You already answered today'})
             
        if not created:
             session.start_time = timezone.now()
             session.save()
             
        return JsonResponse({'success': True, 'follower_id': follower.id})
    return JsonResponse({'success': False}, status=400)

import json
def submit_quiz_answer(request):
    if request.method == 'POST':
        follower_id = request.POST.get('follower_id')
        answers_json = request.POST.get('answers') # e.g. [{"question_id": 1, "option": "A"}]
        
        follower = Follower.objects.filter(id=follower_id).first()
        if not follower:
            return JsonResponse({'success': False, 'error': 'Invalid follower'})
            
        today = timezone.localdate()
        session = DailyQuizSession.objects.filter(follower=follower, active_date=today).first()
        
        if not session or session.is_completed:
            return JsonResponse({'success': False, 'error': 'Session invalid or already completed'})
            
        try:
            answers_data = json.loads(answers_json)
        except Exception:
            answers_data = []
            
        time_taken = (timezone.now() - session.start_time).total_seconds()
        score = 0
        total_questions = DailyQuestion.objects.filter(active_date=today).count()
        
        for ans in answers_data:
            q_id = ans.get('question_id')
            selected = ans.get('option', '').strip()
            q = DailyQuestion.objects.filter(id=q_id, active_date=today).first()
            if q:
                is_correct = (selected == q.correct_option)
                if is_correct:
                    score += 1
                ParticipantAnswer.objects.update_or_create(
                    follower=follower,
                    question=q,
                    defaults={
                        'selected_option': selected,
                        'is_correct': is_correct
                    }
                )
                
        session.time_taken_seconds = time_taken
        session.score = score
        session.is_completed = True
        session.save()
        
    return JsonResponse({'success': False}, status=400)

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from .models import Offering, Follower

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'portal/login.html', {'form': form, 'error': 'Taarifa si sahihi / Invalid credentials'})
    else:
        form = AuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def dashboard_view(request):
    user = request.user
    is_superadmin = user.is_superuser
    
    try:
        country_name = "Dunia Nzima (Global)" if is_superadmin else user.leader_profile.country
    except Exception:
        country_name = "Hakuna Nchi (No Country Assigned)"
        
    from .models import Follower, PrayerRequest, Testimony, Announcement, Offering
    
    if is_superadmin:
        followers = Follower.objects.all().order_by('-created_at')
        requests_qs = PrayerRequest.objects.all().order_by('-created_at')
        testimonies_qs = Testimony.objects.all().order_by('-created_at')
        offerings = Offering.objects.filter(is_verified=True)
    else:
        followers = Follower.objects.filter(country__iexact=country_name).order_by('-created_at')
        requests_qs = PrayerRequest.objects.filter(user_country__iexact=country_name).order_by('-created_at')
        testimonies_qs = Testimony.objects.filter(user_country__iexact=country_name).order_by('-created_at')
        offerings = Offering.objects.filter(country__iexact=country_name, is_verified=True)
        
    from django.core.cache import cache
    import requests
    
    def get_tzs_total(offerings_qs):
        rates = cache.get('exchange_rates_to_tzs')
        if not rates:
            try:
                resp = requests.get('https://api.exchangerate-api.com/v4/latest/TZS', timeout=5)
                if resp.status_code == 200:
                    rates = resp.json().get('rates', {})
                    cache.set('exchange_rates_to_tzs', rates, 86400)
                else:
                    rates = {}
            except Exception:
                rates = {}
                
        fallback_rates = {'TZS': 1.0, 'KES': 20.3, 'UGX': 0.71, 'USD': 2628.0}
        total_tzs = 0.0
        
        currency_totals = offerings_qs.values('currency').annotate(total=Sum('amount'))
        for ct in currency_totals:
            curr = ct['currency']
            amt = float(ct['total'] or 0)
            if curr == 'TZS':
                total_tzs += amt
            else:
                rate = rates.get(curr) if rates else None
                if rate and rate > 0:
                    total_tzs += (amt / rate)
                else:
                    total_tzs += (amt * fallback_rates.get(curr, 1.0))
        return total_tzs

    total_amount = get_tzs_total(offerings)

    context = {
        'is_superadmin': is_superadmin,
        'country_name': country_name,
        'followers_count': followers.count(),
        'requests_count': requests_qs.count(),
        'testimonies_count': testimonies_qs.count(),
        'announcements_count': Announcement.objects.count(),
        'total_amount': total_amount,
        'recent_followers': followers[:5],
        'recent_requests': requests_qs[:5],
    }
    return render(request, 'portal/dashboard.html', context)

@login_required(login_url='/login/')
def dashboard_members_view(request):
    user = request.user
    is_superadmin = user.is_superuser
    
    try:
        leader_country = "Dunia Nzima (Global)" if is_superadmin else user.leader_profile.country
    except Exception:
        leader_country = "Hakuna Nchi (No Country Assigned)"

    if request.method == 'POST' and request.POST.get('action') == 'delete_member':
        member_id = request.POST.get('member_id')
        if member_id:
            Follower.objects.filter(id=member_id).delete()
        return redirect('dashboard_members')

    # Base Queryset
    if is_superadmin:
        followers = Follower.objects.all().order_by('-created_at')
    else:
        followers = Follower.objects.filter(country__iexact=leader_country).order_by('-created_at')

    # Filtering Logic
    filter_country = request.GET.get('country', '').strip()
    filter_gender = request.GET.get('gender', '').strip()

    if is_superadmin and filter_country:
        followers = followers.filter(country__iexact=filter_country)
        
    if filter_gender:
        followers = followers.filter(gender=filter_gender)

    # Get distinct countries for the filter dropdown
    countries = Follower.objects.values_list('country', flat=True).distinct().order_by('country')

    # Statistics
    from django.db.models import Count
    total_global = Follower.objects.count()
    total_in_view = followers.count()
    male_count = followers.filter(gender='M').count()
    female_count = followers.filter(gender='F').count()

    # Chart Data
    if is_superadmin and not filter_country:
        chart_qs = Follower.objects.values('country').annotate(count=Count('id')).order_by('-count')[:5]
        chart_labels = [item['country'] for item in chart_qs]
        chart_data = [item['count'] for item in chart_qs]
        chart_title_sw = "Nchi 5 Zinazoongoza"
        chart_title_en = "Top 5 Countries"
    else:
        chart_labels = ['Male (Mwanaume)', 'Female (Mwanamke)', 'Other (Nyingine)']
        chart_data = [male_count, female_count, followers.filter(gender='O').count()]
        chart_title_sw = "Mgawanyo wa Jinsia"
        chart_title_en = "Gender Distribution"

    context = {
        'is_superadmin': is_superadmin,
        'country_name': leader_country,
        'followers': followers,
        'countries': countries,
        'current_country_filter': filter_country,
        'current_gender_filter': filter_gender,
        'total_global': total_global,
        'total_in_view': total_in_view,
        'male_count': male_count,
        'female_count': female_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'chart_title_sw': chart_title_sw,
        'chart_title_en': chart_title_en,
    }
    return render(request, 'portal/dashboard_members.html', context)

@login_required(login_url='/login/')
def dashboard_offerings_view(request):
    user = request.user
    is_superadmin = user.is_superuser
    
    try:
        country_name = "Dunia Nzima (Global)" if is_superadmin else user.leader_profile.country
    except Exception:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_offering' and is_superadmin:
            off_id = request.POST.get('offering_id')
            if off_id:
                Offering.objects.filter(id=off_id).delete()
            return redirect('dashboard_offerings')
            
        elif action == 'add_manual':
            name = request.POST.get('name', 'Anonymous').strip()
            amount = request.POST.get('amount', '0').strip()
            currency = request.POST.get('currency', 'TZS').strip()
            country = request.POST.get('country', country_name).strip() if is_superadmin else country_name
            
            try:
                amt = float(amount)
                if amt > 0:
                    import uuid
                    Offering.objects.create(
                        donor_name=name,
                        amount=amt,
                        currency=currency,
                        country=country,
                        payment_method='CASH',
                        merchant_reference=str(uuid.uuid4()),
                        is_verified=True
                    )
            except ValueError:
                pass
            return redirect('dashboard_offerings')

    if is_superadmin:
        offerings = Offering.objects.filter(is_verified=True).order_by('-date_received')
    else:
        offerings = Offering.objects.filter(country__iexact=country_name, is_verified=True).order_by('-date_received')
        
    context = {
        'is_superadmin': is_superadmin,
        'country_name': country_name,
        'offerings': offerings,
    }
    return render(request, 'portal/dashboard_offerings.html', context)

from .models import CountryLeader, LeaderProfile

@login_required(login_url='/login/')
def dashboard_leaders_view(request):
    user = request.user
    if not user.is_superuser:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_leader':
            leader_id = request.POST.get('leader_id')
            if leader_id:
                leader = CountryLeader.objects.filter(id=leader_id).first()
                if leader:
                    user_to_delete = leader.user
                    leader.delete()
                    user_to_delete.delete()
            return redirect('dashboard_leaders')
            
        elif action == 'create_crm_leader':
            from django.contrib.auth.models import User
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            country = request.POST.get('country', '').strip()
            
            if username and password and country:
                if not User.objects.filter(username=username).exists():
                    new_user = User.objects.create_user(username=username, password=password)
                    CountryLeader.objects.create(user=new_user, country=country)
            return redirect('dashboard_leaders')
            
        elif action == 'create_public_leader':
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
            return redirect('dashboard_leaders')

        elif action == 'edit_public_leader':
            leader_id = request.POST.get('leader_id')
            if leader_id:
                profile = LeaderProfile.objects.filter(id=leader_id).first()
                if profile:
                    name = request.POST.get('name', '').strip()
                    title = request.POST.get('title', '').strip()
                    bio = request.POST.get('bio', '').strip()
                    new_image = request.FILES.get('image')
                    try:
                        order = int(request.POST.get('order', '0'))
                    except ValueError:
                        order = profile.order

                    if name:
                        profile.name = name
                    if title:
                        title_en, title_sw = translate_text(title)
                        profile.title_en = title_en
                        profile.title_sw = title_sw
                    if bio:
                        bio_en, bio_sw = translate_text(bio)
                        profile.bio_en = bio_en
                        profile.bio_sw = bio_sw
                    if new_image:
                        if profile.image:
                            profile.image.delete(save=False)
                        profile.image = new_image
                    profile.order = order
                    profile.save()
            return redirect('dashboard_leaders')
            
        elif action == 'delete_public_leader':
            leader_id = request.POST.get('leader_id')
            if leader_id:
                profile = LeaderProfile.objects.filter(id=leader_id).first()
                if profile:
                    if profile.image:
                        profile.image.delete(save=False)
                    profile.delete()
            return redirect('dashboard_leaders')

    leaders = CountryLeader.objects.all().select_related('user')
    public_leaders = LeaderProfile.objects.all().order_by('order')
    
    context = {
        'is_superadmin': True,
        'country_name': "Dunia Nzima (Global)",
        'leaders': leaders,
        'public_leaders': public_leaders,
    }
    return render(request, 'portal/dashboard_leaders.html', context)

from django.utils.dateparse import parse_datetime
from django.utils import timezone

@login_required(login_url='/login/')
def dashboard_settings_view(request):
    user = request.user
    if not user.is_superuser:
        return redirect('dashboard')
        
    settings = SystemSetting.get_settings()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_settings':
            settings.google_meet_link = request.POST.get('google_meet_link', '').strip()
            settings.daily_verse_en = request.POST.get('daily_verse_en', '').strip()
            settings.daily_verse_sw = request.POST.get('daily_verse_sw', '').strip()
            
            prayer_time_raw = request.POST.get('prayer_time_utc', '').strip()
            import datetime
            if prayer_time_raw:
                parsed_dt = parse_datetime(prayer_time_raw)
                if parsed_dt:
                    if timezone.is_naive(parsed_dt):
                        parsed_dt = timezone.make_aware(parsed_dt, datetime.timezone.utc)
                    settings.prayer_time_utc = parsed_dt
            
            settings.save()
            return redirect('dashboard_settings')

        elif action == 'update_giving_settings':
            settings.mpesa_lipa_namba = request.POST.get('mpesa_lipa_namba', '').strip()
            settings.tigopesa_lipa_namba = request.POST.get('tigopesa_lipa_namba', '').strip()
            settings.airtel_lipa_namba = request.POST.get('airtel_lipa_namba', '').strip()
            settings.bank_name = request.POST.get('bank_name', '').strip()
            settings.bank_account_number = request.POST.get('bank_account_number', '').strip()
            settings.bank_account_name = request.POST.get('bank_account_name', '').strip()
            settings.paypal_link = request.POST.get('paypal_link', '').strip()
            settings.save()
            return redirect('dashboard_settings')

    context = {
        'is_superadmin': True,
        'country_name': "Dunia Nzima (Global)",
        'settings': settings,
    }
    return render(request, 'portal/dashboard_settings.html', context)

@login_required(login_url='/login/')
def dashboard_content_view(request):
    user = request.user
    if not user.is_superuser:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_announcement':
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            if title and content:
                title_en, title_sw = translate_text(title)
                content_en, content_sw = translate_text(content)
                Announcement.objects.create(title_en=title_en, title_sw=title_sw, content_en=content_en, content_sw=content_sw)
            return redirect('dashboard_content')

        elif action == 'delete_announcement':
            ann_id = request.POST.get('id')
            if ann_id:
                Announcement.objects.filter(id=ann_id).delete()
            return redirect('dashboard_content')

        elif action == 'create_question':
            q_en = request.POST.get('question_en', '').strip()
            q_sw = request.POST.get('question_sw', '').strip()
            active_date = request.POST.get('active_date', '').strip()
            opt_a = request.POST.get('option_a', '').strip()
            opt_b = request.POST.get('option_b', '').strip()
            opt_c = request.POST.get('option_c', '').strip()
            opt_d = request.POST.get('option_d', '').strip()
            correct_opt = request.POST.get('correct_option', 'A').strip()
            
            if q_en and active_date and opt_a and opt_b:
                if not q_sw: q_sw = q_en
                opt_a_en, opt_a_sw = translate_text(opt_a)
                opt_b_en, opt_b_sw = translate_text(opt_b)
                opt_c_en, opt_c_sw = translate_text(opt_c) if opt_c else ("-", "-")
                opt_d_en, opt_d_sw = translate_text(opt_d) if opt_d else ("-", "-")

                DailyQuestion.objects.create(
                    question_text_en=q_en, question_text_sw=q_sw,
                    option_a_en=opt_a_en, option_a_sw=opt_a_sw,
                    option_b_en=opt_b_en, option_b_sw=opt_b_sw,
                    option_c_en=opt_c_en, option_c_sw=opt_c_sw,
                    option_d_en=opt_d_en, option_d_sw=opt_d_sw,
                    correct_option=correct_opt, active_date=active_date
                )
            return redirect('dashboard_content')

        elif action == 'delete_question':
            q_id = request.POST.get('id')
            if q_id:
                DailyQuestion.objects.filter(id=q_id).delete()
            return redirect('dashboard_content')

    announcements = Announcement.objects.all().order_by('-created_at')
    questions = DailyQuestion.objects.all().order_by('-active_date')

    context = {
        'is_superadmin': True,
        'country_name': "Dunia Nzima (Global)",
        'announcements': announcements,
        'questions': questions,
    }
    return render(request, 'portal/dashboard_content.html', context)

@login_required(login_url='/login/')
def dashboard_submissions_view(request):
    user = request.user
    is_superadmin = user.is_superuser
    try:
        country_name = "Dunia Nzima (Global)" if is_superadmin else user.leader_profile.country
    except Exception:
        country_name = "Hakuna Nchi (No Country Assigned)"

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_request':
            req_id = request.POST.get('id')
            if req_id:
                PrayerRequest.objects.filter(id=req_id).delete()
            return redirect('dashboard_submissions')
        elif action == 'delete_testimony':
            test_id = request.POST.get('id')
            if test_id:
                Testimony.objects.filter(id=test_id).delete()
            return redirect('dashboard_submissions')

    if is_superadmin:
        prayer_requests = PrayerRequest.objects.all().order_by('-created_at')
        testimonies = Testimony.objects.all().order_by('-created_at')
    else:
        prayer_requests = PrayerRequest.objects.filter(user_country__iexact=country_name).order_by('-created_at')
        testimonies = Testimony.objects.filter(user_country__iexact=country_name).order_by('-created_at')

    context = {
        'is_superadmin': is_superadmin,
        'country_name': country_name,
        'prayer_requests': prayer_requests,
        'testimonies': testimonies,
    }
    return render(request, 'portal/dashboard_submissions.html', context)

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .pesapal_utils import PesaPalAPI
from django.http import JsonResponse

def giving_checkout(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Anonymous').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        amount = request.POST.get('amount', '0').strip()
        currency = request.POST.get('currency', 'TZS').strip()
        country = request.POST.get('country', 'Tanzania').strip()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid amount.'}, status=400)

        pesapal = PesaPalAPI()
        
        domain = get_current_site(request).domain
        protocol = 'https' if request.is_secure() else 'http'
        base_url = f"{protocol}://{domain}"
        
        ipn_url = f"{base_url}{reverse('pesapal_ipn')}"
        callback_url = f"{base_url}{reverse('pesapal_callback')}"
        
        try:
            system_settings = SystemSetting.get_settings()
            ipn_id = system_settings.pesapal_ipn_id
            if not ipn_id:
                ipn_id = pesapal.register_ipn(ipn_url)
                system_settings.pesapal_ipn_id = ipn_id
                system_settings.save()
                
            response_data = pesapal.submit_order(
                amount=amount,
                currency=currency,
                description="Power Request Offering",
                callback_url=callback_url,
                ipn_id=ipn_id,
                first_name=name,
                email=email,
                phone=phone
            )
            
            Offering.objects.create(
                donor_name=name,
                donor_email=email,
                amount=amount,
                currency=currency,
                country=country,
                payment_method='PESAPAL',
                merchant_reference=response_data['merchant_reference'],
                order_tracking_id=response_data['order_tracking_id'],
                is_verified=False
            )
            
            return JsonResponse({
                'success': True,
                'redirect_url': response_data['redirect_url']
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def pesapal_ipn(request):
    try:
        order_tracking_id = request.GET.get('OrderTrackingId') or request.POST.get('OrderTrackingId')
        
        if order_tracking_id:
            pesapal = PesaPalAPI()
            status_data = pesapal.get_transaction_status(order_tracking_id)
            
            payment_status = status_data.get('payment_status_description', '').upper()
            
            offering = Offering.objects.filter(order_tracking_id=order_tracking_id).first()
            if offering:
                if payment_status == 'COMPLETED':
                    offering.is_verified = True
                    offering.transaction_id = status_data.get('confirmation_code')
                elif payment_status in ['FAILED', 'INVALID']:
                    offering.is_verified = False
                offering.save()
                
            return JsonResponse({'status': 200, 'message': 'IPN Processed'})
    except Exception as e:
        print("IPN Error:", e)
        
    return JsonResponse({'status': 500, 'message': 'Failed'})

def pesapal_callback(request):
    order_tracking_id = request.GET.get('OrderTrackingId')
    
    if order_tracking_id:
        try:
            pesapal = PesaPalAPI()
            status_data = pesapal.get_transaction_status(order_tracking_id)
            payment_status = status_data.get('payment_status_description', '').upper()
            
            offering = Offering.objects.filter(order_tracking_id=order_tracking_id).first()
            if offering:
                if payment_status == 'COMPLETED':
                    offering.is_verified = True
                    offering.transaction_id = status_data.get('confirmation_code')
                offering.save()
                
            context = {'status': payment_status, 'offering': offering}
            return render(request, 'portal/payment_status.html', context)
        except Exception as e:
            context = {'status': 'ERROR', 'error': str(e)}
            return render(request, 'portal/payment_status.html', context)
            
    return redirect('home')

# --- Sermons Views ---
from .models import SermonSeries, SermonLesson

def sermons_list_view(request):
    series = SermonSeries.objects.all().order_by('-created_at')
    context = {'series': series}
    return render(request, 'portal/sermons.html', context)

def sermon_series_detail_view(request, series_id):
    from django.shortcuts import get_object_or_404
    series = get_object_or_404(SermonSeries, id=series_id)
    lessons = series.lessons.all().order_by('order', 'date_preached')
    context = {'series': series, 'lessons': lessons}
    return render(request, 'portal/sermon_series.html', context)

@login_required(login_url='/login/')
def dashboard_sermons_view(request):
    user = request.user
    if not user.is_superuser:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_series':
            title_en = request.POST.get('title_en', '').strip()
            title_sw = request.POST.get('title_sw', '').strip()
            desc_en = request.POST.get('description_en', '').strip()
            desc_sw = request.POST.get('description_sw', '').strip()
            image = request.FILES.get('cover_image')
            
            if title_en or title_sw:
                SermonSeries.objects.create(
                    title_en=title_en, title_sw=title_sw,
                    description_en=desc_en, description_sw=desc_sw,
                    cover_image=image
                )
            return redirect('dashboard_sermons')
            
        elif action == 'delete_series':
            series_id = request.POST.get('series_id')
            series = SermonSeries.objects.filter(id=series_id).first()
            if series:
                if series.cover_image:
                    series.cover_image.delete(save=False)
                series.delete()
            return redirect('dashboard_sermons')
            
        elif action == 'add_lesson':
            series_id = request.POST.get('series_id')
            title_en = request.POST.get('title_en', '').strip()
            title_sw = request.POST.get('title_sw', '').strip()
            preacher = request.POST.get('preacher_name', '').strip()
            media_url = request.POST.get('media_url', '').strip()
            order = request.POST.get('order', '0')
            
            try:
                order_num = int(order)
            except ValueError:
                order_num = 0
                
            if series_id and media_url:
                SermonLesson.objects.create(
                    series_id=series_id,
                    title_en=title_en, title_sw=title_sw,
                    preacher_name=preacher,
                    media_url=media_url,
                    order=order_num
                )
            return redirect('dashboard_sermons')
            
        elif action == 'delete_lesson':
            lesson_id = request.POST.get('lesson_id')
            SermonLesson.objects.filter(id=lesson_id).delete()
            return redirect('dashboard_sermons')

    series = SermonSeries.objects.all().order_by('-created_at')
    context = {
        'is_superadmin': True,
        'country_name': "Dunia Nzima (Global)",
        'series': series,
    }
    return render(request, 'portal/dashboard_sermons.html', context)
