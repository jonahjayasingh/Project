import os
import django
import random
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_backend.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Post, Comment

def seed():
    # Create a user if none exists
    admin_user, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    test_user, _ = User.objects.get_or_create(username='testuser')
    if created:
        test_user.set_password('test1234')
        test_user.save()

    # Create 3 posts
    posts_data = [
        {
            'title': 'The Rise of Modern NLP',
            'content': 'Natural Language Processing has seen exponential growth in the last few years. From Transformers to Large Language Models, the way we interact with machines is changing rapidly. This post explores the core concepts of modern NLP and its applications in safety and moderation.',
            'status': 'published'
        },
        {
            'title': 'Building Safe Communities',
            'content': 'Community moderation is a critical aspect of any online platform. In this article, we discuss how automated tools can help reduce toxicity and create a more inclusive environment for everyone. We will look at both rule-based and AI-driven approaches.',
            'status': 'published'
        },
        {
            'title': 'The Future of Web Development',
            'content': 'With frameworks like Next.js and backend tools like Django, building powerful web applications has never been easier. Today, we delve into how these technologies can be combined with AI to create smarter, more responsive user experiences.',
            'status': 'published'
        }
    ]

    for data in posts_data:
        Post.objects.get_or_create(
            title=data['title'],
            defaults={
                'slug': slugify(data['title']),
                'author': admin_user,
                'content': data['content'],
                'status': data['status']
            }
        )

    all_posts = Post.objects.all()
    
    # 10 Comments (non-bullying)
    comments_content = [
        "Great article! I learned a lot about NLP today.",
        "Very insightful. I agree that community moderation is key.",
        "Django is indeed amazing for backend development.",
        "I'm really excited about the future of AI in web apps.",
        "Thanks for sharing this, it helped me understand the topic better.",
        "This is a well-written post. Looking forward to more!",
        "Transformers are definitely a game-changer.",
        "How do you think LLMs will evolve in the next year?",
        "Excellent points on safety and moderation.",
        "I've been using Django for years and it's still my favorite."
    ]

    for content in comments_content:
        Comment.objects.create(
            post=random.choice(all_posts),
            author=test_user,
            content=content
        )

    print("Successfully seeded 3 posts and 10 comments.")

if __name__ == '__main__':
    seed()
