from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Conversation, Message, Document
from .forms import RegisterForm
from .ai_service import ai_service
import time
import os
import threading

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "chat/login.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = RegisterForm()
    return render(request, "chat/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

def landing_page(request):
    """Landing page for unauthenticated users"""
    if request.user.is_authenticated:
        return redirect("index")
    return render(request, "chat/landing.html")

@login_required
def index(request):
    """Main chat interface"""
    # Cleanup empty conversations before loading
    Conversation.objects.filter(user=request.user, messages__isnull=True).delete()
    
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')[:20]
    current_conversation = conversations.first() if conversations.exists() else None
    
    context = {
        'conversations': conversations,
        'current_conversation': current_conversation,
    }
    return render(request, 'chat/index.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Load a specific conversation"""
    # Cleanup empty conversations EXCEPT the one we are visiting
    Conversation.objects.filter(user=request.user, messages__isnull=True).exclude(id=conversation_id).delete()
    
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')[:20]
    
    context = {
        'conversations': conversations,
        'current_conversation': conversation,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'chat/partials/messages.html', context)
    
    return render(request, 'chat/index.html', context)

@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id=None):
    """Handle sending a message"""
    user_message = request.POST.get('message', '').strip()
    
    if not user_message:
        return HttpResponse('')
    
    # Create or get conversation
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        conversation = Conversation.objects.create(
            user=request.user,
            title=user_message[:50] + ('...' if len(user_message) > 50 else '')
        )
    
    # Save user message
    user_msg = Message.objects.create(
        conversation=conversation,
        role='user',
        content=user_message
    )
    
    # Process any uploaded documents from the chat input
    uploaded_files = request.FILES.getlist('documents')
    if uploaded_files:
        project_root = os.path.dirname(os.path.dirname(__file__))
        book_dir = os.path.join(project_root, "books")
        os.makedirs(book_dir, exist_ok=True)
        
        temp_paths = []
        for f in uploaded_files:
            file_path = os.path.join(book_dir, f"{request.user.id}_{f.name}")
            with open(file_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            temp_paths.append(file_path)
            
            Document.objects.create(
                user=request.user,
                name=f.name,
                file_path=file_path,
                is_global=False # Chat uploads are private by default
            )
        
        # Immediate ingestion (blocking for chat simplicity, or could be background)
        ai_service.ingest_documents(temp_paths, user=request.user, is_global=False)

    # Generate response
    ai_response = generate_ai_response(user_message, request.user)
    
    assistant_msg = Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=ai_response
    )
    
    context = {
        'user_message': user_msg,
        'assistant_message': assistant_msg,
        'conversation': conversation,
    }
    
    response = render(request, 'chat/partials/message_pair.html', context)
    # Trigger both message addition and a sidebar refresh (in case it was the first message)
    response['HX-Trigger'] = 'messageAdded, refreshSidebar'
    return response

@login_required
def new_conversation(request):
    """Create a new conversation - standard redirect"""
    conversation = Conversation.objects.create(user=request.user, title="New Chat")
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
@require_http_methods(["POST", "DELETE"])
def delete_conversation(request, conversation_id):
    """Delete a conversation - Redirect to home"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    return redirect('index')

@login_required
@require_http_methods(["POST"])
def rename_conversation(request, conversation_id):
    """Rename a conversation - Standard redirect"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    new_title = request.POST.get('title', '').strip()
    
    if new_title:
        conversation.title = new_title
        conversation.save()
    
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
@require_http_methods(["POST"])
def clear_conversation(request, conversation_id):
    """Clear all messages in a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.messages.all().delete()
    
    context = {'current_conversation': conversation}
    return render(request, 'chat/partials/messages.html', context)

@login_required
@require_http_methods(["POST"])
def upload_documents(request):
    """Handle document uploads for RAG"""
    uploaded_files = request.FILES.getlist('documents')
    if not uploaded_files:
        messages.error(request, "No files uploaded.")
        return redirect('settings')
    
    temp_paths = []
    # Point to the Website directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    book_dir = os.path.join(project_root, "books")
    os.makedirs(book_dir, exist_ok=True)
    
    is_global = False
    if request.user.is_superuser:
        # Admins can choose to make it global, otherwise default to False
        is_global = request.POST.get('is_global') == 'true' or request.POST.get('is_global') == 'on'
        # If not explicitly set in POST (like from the mini-upload), default to True for admins
        if 'is_global' not in request.POST:
            is_global = True
    
    saved_docs = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(book_dir, f"{request.user.id}_{uploaded_file.name}")
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        temp_paths.append(file_path)
        
        # Create Document record
        doc = Document.objects.create(
            user=request.user,
            name=uploaded_file.name,
            file_path=file_path,
            is_global=is_global
        )
        saved_docs.append(doc)
    
    # Ingest documents in a background thread to allow polling
    def run_ingestion():
        success, message = ai_service.ingest_documents(temp_paths, user=request.user, is_global=is_global)
        # We can't easily use django messages from a thread, 
        # but the progress view will handle the completion UI.
        print(f"Background Ingestion Complete: {message}")

    thread = threading.Thread(target=run_ingestion)
    thread.start()
    
    # Redirect immediately, setting a flag that we are processing
    request.session['is_processing'] = True
    return redirect('settings')

@login_required
def upload_progress(request):
    """API endpoint for HTMX polling of upload progress"""
    progress_data = ai_service.progress.get(request.user.id, {"percentage": 0, "current_file": "Initializing..."})
    
    # Handle both old integer format and new dictionary format for safety
    if isinstance(progress_data, int):
        progress = progress_data
        current_file = "Processing..."
    else:
        progress = progress_data.get("percentage", 0)
        current_file = progress_data.get("current_file", "Processing...")
    
    if progress >= 100:
        # Clear processing flag
        request.session['is_processing'] = False
        from django.contrib import messages
        messages.success(request, "Neural ingestion complete. Your knowledge base has been updated.")
        return HttpResponse("""
            <div id="progress-container" style="text-align: center;">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--accent-primary); margin-bottom: 1.5rem;"></i>
                <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem;">SYNTHESIS SUCCESSFUL</h2>
                <p style="color: var(--text-tertiary); font-weight: 600;">VECTOR PATHS ESTABLISHED</p>
                <script>setTimeout(() => window.location.reload(), 2000);</script>
            </div>
        """)
    
    if progress == -1:
        request.session['is_processing'] = False
        return HttpResponse("""
            <div id="progress-container" style="text-align: center;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ef4444; margin-bottom: 1.5rem;"></i>
                <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; color: #ef4444;">INGESTION FAILED</h2>
                <p style="color: var(--text-tertiary); font-weight: 600;">DATABASE ERROR DETECTED</p>
                <button onclick="window.location.reload()" class="btn" style="margin-top: 2rem; background: rgba(255,255,255,0.05); border: 1px solid var(--border-color);">CONTINUE</button>
            </div>
        """)

    return render(request, 'chat/partials/progress_bar.html', {
        'progress': progress,
        'current_file': current_file
    })

@login_required
def settings_view(request):
    """Settings page"""
    context = {
        'library_books': ai_service.get_library_info(request.user),
        'is_processing': request.session.get('is_processing', False),
    }
    return render(request, 'chat/settings.html', context)

@login_required
@require_http_methods(["POST"])
def clear_library(request):
    """Clear the library for current user"""
    success, message = ai_service.clear_library(request.user)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('settings')

@login_required
@require_http_methods(["POST"])
def delete_document(request, document_id):
    """Delete a specific document"""
    
    if request.user.is_superuser:
        document = get_object_or_404(Document, id=document_id)
    else:
        document = get_object_or_404(Document, id=document_id, user=request.user)
    
    name = document.name
    
    # 1. Remove from Vector DB
    ai_service.delete_document_vectors(name)
    
    # 2. Delete source file from disk
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            print(f"Error removing file: {e}")
            
    # 3. Delete database record
    document.delete()
    
    messages.success(request, f"Document '{name}' deleted successfully.")
    return redirect('settings')

def generate_ai_response(user_message, user):
    """Generate AI response using the AI service"""
    try:
        if not ai_service.llm:
            ai_service.initialize()
        return ai_service.generate_response(user_message, user=user, use_rag=True)
    except Exception as e:
        return f"Error: {str(e)}"
