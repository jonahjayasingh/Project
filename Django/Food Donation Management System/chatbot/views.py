from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import requests
from datetime import datetime
from .models import ChatSession, ChatMessage
from donations.models import Donation

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "cogito-2.1:671b-cloud"

@login_required
def chatbot_view(request):
    """Main chatbot interface"""
    # Get or create active session for user
    session = ChatSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        session = ChatSession.objects.create(user=request.user)
    
    messages = session.messages.all()
    return render(request, 'chatbot/chat.html', {
        'session': session,
        'messages': messages
    })

@login_required
@require_POST
def send_message(request):
    """Handle chat message and get response from Ollama"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create active session
        session = ChatSession.objects.filter(user=request.user, is_active=True).first()
        if not session:
            session = ChatSession.objects.create(user=request.user)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # Build conversation context
        conversation_history = session.messages.all()
        context = build_donation_context(conversation_history)
        
        # Get response from Ollama
        prompt = f"""{context}

User: {user_message}
Assistant:"""
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            assistant_message = response.json().get('response', 'Sorry, I could not process that.')
            
            # Save assistant response
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=assistant_message
            )
            
            # Check if we have all donation details and create donation
            donation_data = extract_donation_data(conversation_history)
            if donation_data and all(donation_data.values()):
                create_donation_from_chat(request.user, donation_data)
                return JsonResponse({
                    'response': assistant_message,
                    'donation_created': True
                })
            
            return JsonResponse({'response': assistant_message})
        else:
            return JsonResponse({'error': 'Failed to get response from chatbot'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def new_session(request):
    """Create a new chat session"""
    # Deactivate current session
    ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    # Create new session
    ChatSession.objects.create(user=request.user)
    
    return redirect('chatbot')

def build_donation_context(messages):
    """Build context for donation collection"""
    context = """You are a helpful assistant for a Food Donation Management System. 
Your job is to collect donation details from donors in a friendly, conversational manner.

You need to collect the following information:
1. Food type (e.g., rice, vegetables, cooked meals)
2. Quantity (e.g., 5 kg, 10 servings)
3. Cooked time (when the food was cooked, if applicable)
4. Pickup time (when the food can be picked up)
5. Location (latitude and longitude, or ask for address)

Ask for one detail at a time. Be friendly and conversational.
When you have all the details, confirm with the user and let them know the donation will be created.

Previous conversation:"""
    
    for msg in list(messages)[-10:]:  # Last 10 messages for context
        context += f"\n{msg.role.capitalize()}: {msg.content}"
    
    return context

def extract_donation_data(messages):
    """Extract donation data from conversation"""
    # This is a simplified extraction
    # In production, you'd use NLP or structured prompts
    data = {
        'food_type': None,
        'quantity': None,
        'cooked_time': None,
        'pickup_time': None,
        'latitude': None,
        'longitude': None
    }
    
    # Basic keyword extraction (simplified)
    conversation_text = ' '.join([msg.content for msg in messages])
    
    # This would need more sophisticated parsing in production
    # For now, return None to indicate manual form should be used
    return None

def create_donation_from_chat(user, donation_data):
    """Create donation from extracted chat data"""
    Donation.objects.create(
        donor=user,
        food_type=donation_data['food_type'],
        quantity=donation_data['quantity'],
        cooked_time=donation_data.get('cooked_time'),
        pickup_time=donation_data['pickup_time'],
        latitude=donation_data.get('latitude'),
        longitude=donation_data.get('longitude'),
        status='Pending'
    )
