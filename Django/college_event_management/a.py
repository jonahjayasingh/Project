import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "college_event_management.settings")
django.setup()
from Coordinator.models import Mcq,Question
from django.contrib.auth.models import User


data = {'formName': 'mcc test', 'questionCount': 3, 'questions': [{'number': '1', 'text': 'a', 'correctAnswer': '2', 'options': [{'number': 1, 'text': '1'}, {'number': 2, 'text': '2'}, {'number': 3, 'text': '3'}, {'number': 4, 'text': '4'}]}, {'number': '2', 'text': 'b', 'correctAnswer': '2', 'options': [{'number': 1, 'text': '1'}, {'number': 2, 'text': '2'}, {'number': 3, 'text': '3'}, {'number': 4, 'text': '4'}]}, {'number': '3', 'text': 'c', 'correctAnswer': '2', 'options': [{'number': 1, 'text': '1'}, {'number': 2, 'text': '2'}, {'number': 3, 'text': '3'}, {'number': 4, 'text': '4'}]}]}
print(data['formName'])
print(data['questionCount'])
mcq  = Mcq.objects.create(user=User.objects.get(username="admin"),mcq_title=data['formName'],no_of_questions=data['questionCount'])

for q in data['questions']:
    Question.objects.create(
        mcq=mcq,
        question=q['text'],
        option1=q['options'][0]['text'],
        option2=q['options'][1]['text'],
        option3=q['options'][2]['text'],
        option4=q['options'][3]['text'],
        answer=q['correctAnswer']
    )
