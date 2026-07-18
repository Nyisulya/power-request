from django.core.management.base import BaseCommand
from django.utils import timezone
from portal.models import DailyQuestion

class Command(BaseCommand):
    help = 'Creates 5 sample daily questions for today'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        
        sample_questions = [
            {
                'question_en': "In the beginning, what did God create?",
                'question_sw': "Hapo mwanzo Mungu aliumba nini?",
                'opt_a_en': "Animals and Plants", 'opt_a_sw': "Wanyama na Mimea",
                'opt_b_en': "Heavens and Earth", 'opt_b_sw': "Mbingu na Nchi",
                'opt_c_en': "Sun and Moon", 'opt_c_sw': "Jua na Mwezi",
                'opt_d_en': "Man and Woman", 'opt_d_sw': "Mwanamume na Mwanamke",
                'correct': "B"
            },
            {
                'question_en': "Who built the Ark?",
                'question_sw': "Nani alijenga Safina?",
                'opt_a_en': "Moses", 'opt_a_sw': "Musa",
                'opt_b_en': "Abraham", 'opt_b_sw': "Ibrahimu",
                'opt_c_en': "Noah", 'opt_c_sw': "Nuhu",
                'opt_d_en': "David", 'opt_d_sw': "Daudi",
                'correct': "C"
            },
            {
                'question_en': "How many days did Jesus fast in the wilderness?",
                'question_sw': "Yesu alifunga siku ngapi jangwani?",
                'opt_a_en': "30 Days", 'opt_a_sw': "Siku 30",
                'opt_b_en': "40 Days", 'opt_b_sw': "Siku 40",
                'opt_c_en': "10 Days", 'opt_c_sw': "Siku 10",
                'opt_d_en': "7 Days", 'opt_d_sw': "Siku 7",
                'correct': "B"
            },
            {
                'question_en': "Which sea did Moses part?",
                'question_sw': "Musa alitenganisha bahari gani?",
                'opt_a_en': "Red Sea", 'opt_a_sw': "Bahari ya Shamu",
                'opt_b_en': "Dead Sea", 'opt_b_sw': "Bahari ya Chumvi",
                'opt_c_en': "Mediterranean Sea", 'opt_c_sw': "Bahari ya Mediterania",
                'opt_d_en': "Black Sea", 'opt_d_sw': "Bahari Nyeusi",
                'correct': "A"
            },
            {
                'question_en': "What is the first book of the New Testament?",
                'question_sw': "Kitabu cha kwanza cha Agano Jipya ni kipi?",
                'opt_a_en': "Mark", 'opt_a_sw': "Marko",
                'opt_b_en': "Luke", 'opt_b_sw': "Luka",
                'opt_c_en': "John", 'opt_c_sw': "Yohana",
                'opt_d_en': "Matthew", 'opt_d_sw': "Mathayo",
                'correct': "D"
            }
        ]

        for q in sample_questions:
            DailyQuestion.objects.create(
                active_date=today,
                question_text_en=q['question_en'],
                question_text_sw=q['question_sw'],
                option_a_en=q['opt_a_en'], option_a_sw=q['opt_a_sw'],
                option_b_en=q['opt_b_en'], option_b_sw=q['opt_b_sw'],
                option_c_en=q['opt_c_en'], option_c_sw=q['opt_c_sw'],
                option_d_en=q['opt_d_en'], option_d_sw=q['opt_d_sw'],
                correct_option=q['correct']
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully created 5 sample questions for {today}!"))
