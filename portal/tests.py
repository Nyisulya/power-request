from django.test import TestCase
from django.urls import reverse
from .models import SystemSetting, PrayerRequest, Testimony, Announcement, Follower
from .translator import translate_text

class TranslationTest(TestCase):
    def test_translate_empty(self):
        self.assertEqual(translate_text(""), ("", ""))
        self.assertEqual(translate_text(None), ("", ""))

    def test_translate_basic(self):
        # Even if deep-translator fails/succeeds, it should return strings
        en, sw = translate_text("Hello")
        self.assertIsInstance(en, str)
        self.assertIsInstance(sw, str)

class ModelTestCase(TestCase):
    def test_settings_singleton(self):
        s1 = SystemSetting.get_settings()
        s2 = SystemSetting.get_settings()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(SystemSetting.objects.count(), 1)

        # Update and save another setting to check persistence
        s2.google_meet_link = "https://meet.google.com/test-meet"
        s2.save()
        
        self.assertEqual(SystemSetting.objects.count(), 1)
        s3 = SystemSetting.get_settings()
        self.assertEqual(s3.google_meet_link, "https://meet.google.com/test-meet")

class ViewsTestCase(TestCase):
    def setUp(self):
        self.settings = SystemSetting.get_settings()
        self.settings.daily_verse_en = "God is good"
        self.settings.daily_verse_sw = "Mungu ni mwema"
        self.settings.save()

    def test_home_page_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "God is good")
        self.assertContains(response, "Mungu ni mwema")

    def test_submit_request_success(self):
        url = reverse('submit_request')
        post_data = {
            'author_name': 'Test User',
            'content': 'Tafadhali niombee',
            'user_country': 'Tanzania'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['author_name'], 'Test User')
        self.assertEqual(json_data['user_country'], 'Tanzania')
        
        # Verify it saved in database
        self.assertEqual(PrayerRequest.objects.count(), 1)
        req = PrayerRequest.objects.first()
        self.assertEqual(req.author_name, 'Test User')

    def test_submit_testimony_success(self):
        url = reverse('submit_testimony')
        post_data = {
            'author_name': 'Test Witness',
            'content': 'Mungu amenitendea mema',
            'user_country': 'Kenya'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        
        self.assertEqual(Testimony.objects.count(), 1)
        testi = Testimony.objects.first()
        self.assertEqual(testi.author_name, 'Test Witness')

    def test_leader_panel_auth(self):
        # 1. Unauthenticated leader page access
        url = reverse('leader_panel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leader Verification")
        self.assertNotContains(response, "Global Settings")

        # 2. Failed authentication
        post_data = {
            'action': 'login',
            'passcode': 'wrong_passcode'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenosiri si sahihi")

        # 3. Successful authentication
        post_data['passcode'] = 'power2026'
        response = self.client.post(url, post_data)
        # Should redirect to leader_panel
        self.assertRedirects(response, url)
        
        # Now access the leader panel GET request - should show configuration settings
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Global Settings")
        self.assertContains(response, "Daily Verse (English)")

    def test_about_page_view(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pastor Joel Mkombozi")
        self.assertContains(response, "Sister Sarah Kavishe")

    def test_requests_room_view(self):
        url = reverse('requests_room')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prayer Sanctuary")

    def test_testimonies_room_view(self):
        url = reverse('testimonies_room')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testimony Sanctuary")

    def test_giving_page_view(self):
        self.settings.mpesa_lipa_namba = "998877"
        self.settings.bank_account_number = "555-555-555"
        self.settings.save()

        url = reverse('giving')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "998877")
        self.assertContains(response, "555-555-555")

    def test_leader_create_announcement_and_delete(self):
        session = self.client.session
        session['is_leader'] = True
        session.save()

        url = reverse('leader_panel')
        post_data = {
            'action': 'create_announcement',
            'title': 'Test Notice',
            'content': 'We are gathering soon.'
        }
        response = self.client.post(url, post_data)
        self.assertRedirects(response, url)

        self.assertEqual(Announcement.objects.count(), 1)
        ann = Announcement.objects.first()
        self.assertEqual(ann.title_en, 'Test Notice')

        post_data = {
            'action': 'delete_announcement',
            'id': ann.id
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Announcement.objects.count(), 0)

    def test_submit_registration_and_delete_follower(self):
        # 1. Post registration
        url = reverse('submit_registration')
        post_data = {
            'full_name': 'Global Follower',
            'email': 'follower@example.com',
            'phone_number': '+255700000000',
            'country': 'Tanzania'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Follower.objects.count(), 1)
        
        fol = Follower.objects.first()
        self.assertEqual(fol.full_name, 'Global Follower')

        # 2. Leader login and delete follower
        session = self.client.session
        session['is_leader'] = True
        session.save()

        leader_url = reverse('leader_panel')
        delete_data = {
            'action': 'delete_follower',
            'id': fol.id
        }
        response = self.client.post(leader_url, delete_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Follower.objects.count(), 0)
