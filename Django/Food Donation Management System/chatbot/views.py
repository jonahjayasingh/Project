from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import json
import requests
from datetime import timedelta
from django.utils import timezone

from .models import ChatSession, ChatMessage
from donations.models import Donation


OLLAMA_API_URL = "http://localhost:11434"
MODEL_NAME = "cogito-2.1:671b-cloud"


# =========================================================
# MAIN CHAT PAGE
# =========================================================

@login_required
def chatbot_view(request):

    session = ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not session:
        session = ChatSession.objects.create(user=request.user)

    return render(request, "chatbot/chat.html", {
        "session": session,
        "chat_messages": session.messages.all()
    })


# =========================================================
# NEW SESSION
# =========================================================

@login_required
def new_session(request):
    ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).update(is_active=False)

    ChatSession.objects.create(user=request.user)

    return redirect("chatbot")


# =========================================================
# SAVE ASSISTANT MESSAGE
# =========================================================

def save_reply(session, text):
    ChatMessage.objects.create(
        session=session,
        role="assistant",
        content=text
    )
    return JsonResponse({"response": text})


# =========================================================
# OLLAMA — STRUCTURED EXTRACTION
# =========================================================

def extract_info(user_message, last_assistant_msg=""):

    prompt = f"""
Analyze this user message for a Food Donation System.
Previous Assistant Message: "{last_assistant_msg}"
User Message: "{user_message}"

Return ONLY JSON:
{{
  "food_type": "string or null",
  "quantity": "string or null",
  "pickup_time": "string or null",
  "intent": "donate / confirm / chat / greeting",
  "is_confirmation": true/false
}}

Note: If the user says "yes", "correct", "confirm", or "ok" in response to a confirmation request, set is_confirmation to true.
"""

    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        },
        timeout=60
    )

    if response.status_code != 200:
        return {}

    try:
        content = response.json()["response"]
        return json.loads(content)
    except:
        return {}


# =========================================================
# OLLAMA — CONVERSATIONAL RESPONSE
# =========================================================

def generate_conversation(user_message, session):

    history = "\n".join(
        f"{m.role}: {m.content}" for m in list(session.messages.all())[-8:]
    )

    state = f"""
Current Status:
- Food: {session.food_type or 'Not yet known'}
- Quantity: {session.quantity or 'Not yet known'}
- Pickup Time: {session.pickup_time or 'Not yet known'}
- Awaiting Confirmation: {session.awaiting_confirmation}
"""

    prompt = f"""
You are a warm, friendly assistant for a Food Donation System.

Goals:
- Have natural conversation
- Encourage food donation
- Ask for missing details politely
- Keep responses short and human-like

{state}

Conversation:
{history}

User: {user_message}
Assistant:
"""

    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    if response.status_code == 200:
        return response.json().get("response", "I'm here to help.")

    return "Sorry, I couldn't respond right now."


# =========================================================
# SEND MESSAGE — CONVERSATIONAL LOGIC
# =========================================================

@login_required
@require_POST
def send_message(request):

    data = json.loads(request.body)
    user_message = data.get("message", "").strip()
    location = data.get("location")

    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    session = ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not session:
        session = ChatSession.objects.create(user=request.user)

    # Save user message
    ChatMessage.objects.create(
        session=session,
        role="user",
        content=user_message
    )

    # =====================================================
    # STEP 1 — EXTRACT INFO SILENTLY
    # =====================================================
    last_reply = session.messages.filter(role='assistant').last()
    last_assistant_text = last_reply.content if last_reply else ""
    
    info = extract_info(user_message, last_assistant_text)

    food = info.get("food_type")
    quantity = info.get("quantity")
    pickup_time = info.get("pickup_time")
    intent = info.get("intent")
    is_confirm = info.get("is_confirmation")
    
    # Keyword fallback for robustness
    if not is_confirm:
        confirm_words = ['yes', 'yeah', 'confirm', 'correct', 'ok', 'okay', 'sure']
        is_confirm = any(word == user_message.lower().strip() for word in confirm_words)

    # Update details if found (allows changing mind)
    if food:
        session.food_type = food
    if quantity:
        session.quantity = quantity
    if pickup_time:
        session.pickup_time = pickup_time

    session.save()

    # =====================================================
    # STEP 2 — CONFIRMATION FLOW
    # =====================================================

    if session.food_type and session.quantity and session.pickup_time and not session.awaiting_confirmation:

        session.awaiting_confirmation = True
        session.save()

        return save_reply(
            session,
            f"Great! You want to donate {session.quantity} of {session.food_type} for pickup at {session.pickup_time}. "
            f"Please confirm so I can arrange pickup. "
            f"Just say 'confirm donation'."
        )

    # =====================================================
    # STEP 3 — CREATE DONATION
    # =====================================================

    if session.awaiting_confirmation and (is_confirm or intent == "confirm"):

        if session.donation_created:
            return save_reply(session, "Donation already created.")

        address = (
            location.get("address")
            if location and location.get("address")
            else getattr(request.user, "address", "Address from chat")
        )

        donation = Donation.objects.create(
            donor=request.user,
            food_type=session.food_type,
            quantity=session.quantity,
            cooked_time=timezone.now(),
            pickup_time=timezone.now() + timedelta(hours=2), # Default if parsing fails
            address=address,
            latitude=location.get("lat") if location else None,
            longitude=location.get("lon") if location else None,
            status="Pending"
        )
        
        # Log Activity and Send Email
        from donations.utils import send_donation_email, log_system_activity
        log_system_activity("Donation Created", request.user, f"Donation #{donation.id} created via AI Assistant")
        send_donation_email(
            "Donation Created",
            "donation_created",
            {'donation': donation},
            [request.user.email]
        )

        # Create status history
        from tracking.models import StatusHistory
        StatusHistory.objects.create(
            donation=donation,
            status='Pending',
            changed_by=request.user,
            notes='Donation created via AI Assistant'
        )

        session.donation_created = True
        session.is_active = False
        session.save()

        return save_reply(
            session,
            "✅ Your donation has been scheduled! Thank you for helping people in need."
        )

    # =====================================================
    # STEP 4 — NORMAL CONVERSATION
    # =====================================================

    reply = generate_conversation(user_message, session)

    return save_reply(session, reply)