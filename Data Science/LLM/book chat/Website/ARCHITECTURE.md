# 📊 Project Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Chat Interface                         │   │
│  │  ┌─────────────┐  ┌──────────────────────────────────┐  │   │
│  │  │  Sidebar    │  │      Main Chat Area              │  │   │
│  │  │             │  │  ┌────────────────────────────┐  │  │   │
│  │  │ + New Chat  │  │  │  User Message              │  │  │   │
│  │  │             │  │  │  AI Response               │  │  │   │
│  │  │ Convos List │  │  │  ...                       │  │  │   │
│  │  │             │  │  └────────────────────────────┘  │  │   │
│  │  │ User Info   │  │  ┌────────────────────────────┐  │  │   │
│  │  └─────────────┘  │  │  Message Input             │  │  │   │
│  │                    │  └────────────────────────────┘  │  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕ HTMX (AJAX)                       │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO WEB SERVER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    URL Routing                            │   │
│  │  /                          → index                       │   │
│  │  /conversation/<id>/        → conversation_detail         │   │
│  │  /conversation/new/         → new_conversation            │   │
│  │  /conversation/<id>/delete/ → delete_conversation         │   │
│  │  /conversation/<id>/rename/ → rename_conversation         │   │
│  │  /message/send/             → send_message                │   │
│  │  /upload/                   → upload_documents            │   │
│  │  /settings/                 → settings_view               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Views Layer                            │   │
│  │  • Process HTTP requests                                  │   │
│  │  • Call AI service                                        │   │
│  │  • Render templates                                       │   │
│  │  • Return HTMX partials                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    AI Service                             │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  generate_response()                               │  │   │
│  │  │    ↓                                                │  │   │
│  │  │  if use_rag:                                        │  │   │
│  │  │    → _generate_rag_response()                       │  │   │
│  │  │  else:                                              │  │   │
│  │  │    → _generate_simple_response()                    │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Models Layer                           │   │
│  │  • Conversation (title, timestamps)                       │   │
│  │  • Message (role, content, conversation FK)               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   SQLite     │  │  ChromaDB    │  │      Ollama          │  │
│  │              │  │              │  │                      │  │
│  │ Conversations│  │   Vectors    │  │  LLM (llava:7b)      │  │
│  │   Messages   │  │  Embeddings  │  │  Embeddings Model    │  │
│  │              │  │  Documents   │  │  (nomic-embed-text)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Sends Message
```
User Input → HTMX Request → Django View → AI Service
                                              ↓
                                         Ollama LLM
                                              ↓
                                         AI Response
                                              ↓
Django View → HTMX Partial → Browser → Display Message
```

### 2. RAG-Enhanced Response
```
User Question → AI Service → Vector Search (ChromaDB)
                                    ↓
                            Retrieve Relevant Chunks
                                    ↓
                            Build Context Prompt
                                    ↓
                            Ollama LLM (with context)
                                    ↓
                            Contextual Answer
```

### 3. Document Upload
```
User Uploads File → Django View → Save to books/
                                        ↓
                                   AI Service
                                        ↓
                                  Load Document
                                        ↓
                                  Split into Chunks
                                        ↓
                              Generate Embeddings (Ollama)
                                        ↓
                              Store in ChromaDB (book_db/)
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    HTML     │  │     CSS     │  │    JavaScript       │ │
│  │  Templates  │  │   Styles    │  │  + HTMX             │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP/AJAX
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Django)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    URLs     │→ │    Views    │→ │      Models         │ │
│  │   Routing   │  │   Logic     │  │   Database ORM      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                          ↓                                   │
│                  ┌─────────────────┐                         │
│                  │   AI Service    │                         │
│                  │  (ai_service.py)│                         │
│                  └─────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                    AI/ML Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  LangChain  │→ │   Ollama    │→ │     ChromaDB        │ │
│  │  Framework  │  │   LLM API   │  │  Vector Storage     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## File Organization

```
Website/
├── chat/                          # Django App
│   ├── __init__.py
│   ├── admin.py                   # Admin configuration
│   ├── apps.py                    # App configuration
│   ├── models.py                  # Data models
│   │   ├── Conversation
│   │   └── Message
│   ├── views.py                   # View functions
│   │   ├── index()
│   │   ├── conversation_detail()
│   │   ├── send_message()
│   │   ├── new_conversation()
│   │   ├── delete_conversation()
│   │   ├── rename_conversation()
│   │   ├── clear_conversation()
│   │   ├── upload_documents()
│   │   ├── settings_view()
│   │   └── clear_library()
│   ├── urls.py                    # URL patterns
│   ├── ai_service.py              # AI/RAG logic
│   │   ├── AIService class
│   │   ├── generate_response()
│   │   ├── ingest_documents()
│   │   └── get_library_info()
│   ├── static/chat/
│   │   ├── css/
│   │   │   ├── style.css          # Main styles
│   │   │   ├── settings.css       # Settings page
│   │   │   └── animations.css     # Animations
│   │   └── js/
│   │       └── script.js          # All JavaScript
│   └── templates/chat/
│       ├── index.html             # Main page
│       ├── settings.html          # Settings page
│       └── partials/
│           ├── messages.html      # Message list
│           ├── message_pair.html  # Single message
│           └── sidebar.html       # Conversation list
├── chatgpt_clone/                 # Django Project
│   ├── settings.py                # Project settings
│   ├── urls.py                    # Root URLs
│   └── wsgi.py                    # WSGI config
├── books/                         # Uploaded documents
├── book_db/                       # Vector database
├── db.sqlite3                     # SQLite database
├── manage.py                      # Django CLI
├── requirements.txt               # Dependencies
├── setup.sh                       # Setup script
├── README.md                      # Documentation
├── FEATURES.md                    # Feature list
├── TROUBLESHOOTING.md             # Help guide
├── SUMMARY.md                     # Completion summary
└── ARCHITECTURE.md                # This file
```

## Technology Stack Details

### Frontend Stack
```
┌─────────────────────────────────────┐
│          User Interface             │
├─────────────────────────────────────┤
│ HTML5         │ Structure           │
│ CSS3          │ Styling             │
│ JavaScript    │ Interactivity       │
│ HTMX          │ AJAX/Dynamic        │
│ Font Awesome  │ Icons               │
│ Google Fonts  │ Typography (Inter)  │
└─────────────────────────────────────┘
```

### Backend Stack
```
┌─────────────────────────────────────┐
│         Application Layer           │
├─────────────────────────────────────┤
│ Django 5.x    │ Web Framework       │
│ Python 3.8+   │ Language            │
│ SQLite        │ Database            │
│ Django ORM    │ Database Access     │
└─────────────────────────────────────┘
```

### AI/ML Stack
```
┌─────────────────────────────────────┐
│           AI/ML Layer               │
├─────────────────────────────────────┤
│ LangChain     │ RAG Framework       │
│ Ollama        │ LLM Inference       │
│ ChromaDB      │ Vector Database     │
│ llava:7b      │ Language Model      │
│ nomic-embed   │ Embedding Model     │
└─────────────────────────────────────┘
```

## Request/Response Cycle

### Standard Chat Message
```
1. User types message and presses Enter
   ↓
2. JavaScript captures form submission
   ↓
3. HTMX sends POST request to /message/send/
   ↓
4. Django view receives request
   ↓
5. View calls AI service generate_response()
   ↓
6. AI service queries Ollama LLM
   ↓
7. LLM generates response
   ↓
8. View creates Message objects (user + AI)
   ↓
9. View renders message_pair.html partial
   ↓
10. HTMX receives HTML response
    ↓
11. HTMX appends to messages container
    ↓
12. JavaScript scrolls to bottom
```

### RAG-Enhanced Message
```
1. User asks question about documents
   ↓
2. Same steps 1-5 as above
   ↓
6. AI service performs vector search in ChromaDB
   ↓
7. Retrieve top-k relevant document chunks
   ↓
8. Build context prompt with retrieved chunks
   ↓
9. Send context + question to Ollama LLM
   ↓
10. LLM generates contextual response
    ↓
11-12. Same as steps 8-12 above
```

## Database Schema

```sql
-- Conversation Table
CREATE TABLE chat_conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

-- Message Table
CREATE TABLE chat_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(10) CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversation(id)
);

-- Indexes
CREATE INDEX idx_conversation_updated ON chat_conversation(updated_at DESC);
CREATE INDEX idx_message_conversation ON chat_message(conversation_id);
CREATE INDEX idx_message_created ON chat_message(created_at);
```

## Vector Database Structure

```
book_db/
├── chroma.sqlite3              # ChromaDB metadata
└── [collection_id]/
    ├── data_level0.bin         # Vector data
    ├── header.bin              # Collection header
    ├── length.bin              # Document lengths
    └── link_lists.bin          # HNSW graph
```

---

This architecture provides:
- ✅ Separation of concerns
- ✅ Scalable design
- ✅ Easy to maintain
- ✅ Clear data flow
- ✅ Modular components
