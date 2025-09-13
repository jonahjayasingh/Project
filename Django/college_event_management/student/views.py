from django.shortcuts import render
from Coordinator.models import Mcq
import json
# Create your views here.
mcq_questions = [
    {
        "question": "What is the capital of France?",
        "options": {
            "A": "Berlin",
            "B": "Madrid",
            "C": "Paris",
            "D": "Rome"
        },
        "answer": "C"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": {
            "A": "Earth",
            "B": "Mars",
            "C": "Jupiter",
            "D": "Saturn"
        },
        "answer": "B"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": {
            "A": "William Shakespeare",
            "B": "Mark Twain",
            "C": "Charles Dickens",
            "D": "Jane Austen"
        },
        "answer": "A"
    },
    {
        "question": "What is the boiling point of water?",
        "options": {
            "A": "90°C",
            "B": "100°C",
            "C": "120°C",
            "D": "80°C"
        },
        "answer": "B"
    },
    {
        "question": "Which gas do plants use for photosynthesis?",
        "options": {
            "A": "Oxygen",
            "B": "Nitrogen",
            "C": "Carbon Dioxide",
            "D": "Hydrogen"
        },
        "answer": "C"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": {
            "A": "Atlantic Ocean",
            "B": "Indian Ocean",
            "C": "Pacific Ocean",
            "D": "Arctic Ocean"
        },
        "answer": "C"
    },
    {
        "question": "Which language is primarily spoken in Brazil?",
        "options": {
            "A": "Spanish",
            "B": "Portuguese",
            "C": "French",
            "D": "English"
        },
        "answer": "B"
    },
    {
        "question": "What is the square root of 64?",
        "options": {
            "A": "6",
            "B": "7",
            "C": "8",
            "D": "9"
        },
        "answer": "C"
    },
    {
        "question": "In which continent is Egypt located?",
        "options": {
            "A": "Asia",
            "B": "Africa",
            "C": "Europe",
            "D": "South America"
        },
        "answer": "B"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": {
            "A": "Leonardo da Vinci",
            "B": "Pablo Picasso",
            "C": "Vincent Van Gogh",
            "D": "Claude Monet"
        },
        "answer": "A"
    }
]


mcq = {
    "mcq_title": "MCQ Exam",
    "mcq_duration": 1,

    "mcq_questions": mcq_questions
}
def index(request):
    mcq = Mcq.objects.get(id=10)
    questions = {}
    for question in mcq.questions.all():
        questions[question.question] = question.get_options()
    print(len(questions))
    return render(request,"student/dashboard.html")

def mcq_exam(request):
    mcq = Mcq.objects.get(id=10)
    questions = {}
    for question in mcq.questions.all():
        questions[question.question] = question.get_options()
    mcq = {
        "mcq_title": mcq.mcq_title,
        "mcq_duration": 1,

        "mcq_questions": questions
    }
    context = {
        "mcq": mcq,
        # "total_questions": len(questions)
    }
    return render(request,"student/mcq_exam.html",context)
