# DocuChat AI - RAG-Powered AI Assistant

A beautiful, feature-rich AI assistant built with Django, HTMX, and LangChain. This application provides an intelligent chat experience with Retrieval-Augmented Generation (RAG) capabilities, allowing you to chat with your own documents.

## ✨ Features

### Core Chat Features
- 💬 **Real-time Chat Interface** - Beautiful, responsive chat UI similar to ChatGPT
- 🔄 **HTMX Integration** - Smooth, dynamic updates without page reloads
- 📝 **Conversation Management** - Create, rename, clear, and delete conversations
- 💾 **Persistent Conversations** - All chats are saved to the database
- 🎨 **Modern Dark Theme** - Sleek, professional design with smooth animations

### AI & RAG Features
- 🤖 **Ollama Integration** - Local AI inference using Ollama
- 📚 **Document Upload** - Upload PDF and TXT files to create a knowledge base
- 🧠 **RAG-Powered Responses** - AI answers questions based on your uploaded documents
- 🔍 **Vector Search** - ChromaDB for efficient semantic search
- 📊 **Library Management** - View and manage your document library

### User Experience
- ⚡ **Fast & Responsive** - Optimized for performance
- 📱 **Mobile Friendly** - Works great on all devices
- ⌨️ **Keyboard Shortcuts** - Enter to send, Shift+Enter for new line
- 🎯 **Auto-scroll** - Automatically scrolls to latest messages
- 🔧 **Settings Page** - Manage AI models and library

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Ollama model downloaded (e.g., `ollama pull llava:7b`)

### Installation

1. **Clone the repository**
   ```bash
   cd Website
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser**
   Navigate to `http://127.0.0.1:8000/`

## 📖 Usage

### Basic Chat
1. Click "New Chat" to start a conversation
2. Type your message and press Enter
3. The AI will respond using the configured Ollama model

### Using RAG (Document-Based Chat)
1. Go to Settings (gear icon in header)
2. Upload PDF or TXT files in the "Library Management" section
3. Click "Upload & Process" to ingest the documents
4. Return to chat and ask questions about your documents
5. The AI will use your documents to provide accurate answers

### Managing Conversations
- **Rename**: Click the three-dot menu → Rename
- **Clear**: Click the three-dot menu → Clear (removes all messages)
- **Delete**: Click the three-dot menu → Delete (removes entire conversation)

## 🏗️ Project Structure

```
Website/
├── chat/                       # Main chat application
│   ├── ai_service.py          # RAG and AI integration
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   ├── static/chat/           # Static files
│   │   ├── css/
│   │   │   ├── style.css      # Main styles
│   │   │   └── settings.css   # Settings page styles
│   │   └── js/
│   │       └── script.js      # JavaScript functionality
│   └── templates/chat/        # HTML templates
│       ├── index.html         # Main chat page
│       ├── settings.html      # Settings page
│       └── partials/          # HTMX partials
├── chatgpt_clone/             # Django project settings
├── books/                     # Uploaded documents (auto-created)
├── book_db/                   # Vector database (auto-created)
├── db.sqlite3                 # SQLite database
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## 🎨 Features in Detail

### Conversation Management
- Create unlimited conversations
- Each conversation maintains its own message history
- Conversations are automatically titled based on first message
- Rename conversations for better organization
- Clear messages while keeping the conversation
- Delete conversations you no longer need

### Document Processing
- Supports PDF and TXT files
- Automatic text extraction and chunking
- Vector embeddings using Ollama's nomic-embed-text
- Efficient storage in ChromaDB
- View all uploaded documents in settings
- Clear entire library when needed

### AI Integration
- Uses Ollama for local, private AI inference
- Configurable model selection
- Context-aware responses
- RAG-enhanced answers from your documents
- Fallback to general chat when no documents match

## 🔧 Configuration

### Changing the AI Model
Edit `chat/ai_service.py`:
```python
DEFAULT_LLM_MODEL = "llava:7b"  # Change to your preferred model
```

### Adjusting Chunk Size
Edit `chat/ai_service.py`:
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,      # Adjust chunk size
    chunk_overlap=120,   # Adjust overlap
)
```

## 🛠️ Technology Stack

- **Backend**: Django 5.x
- **Frontend**: HTML, CSS, JavaScript
- **Dynamic Updates**: HTMX
- **AI Framework**: LangChain
- **LLM**: Ollama
- **Vector Database**: ChromaDB
- **Embeddings**: Ollama nomic-embed-text
- **Database**: SQLite (default)

## 📝 API Endpoints

- `/` - Main chat interface
- `/conversation/<id>/` - Load specific conversation
- `/conversation/new/` - Create new conversation
- `/conversation/<id>/delete/` - Delete conversation
- `/conversation/<id>/rename/` - Rename conversation
- `/conversation/<id>/clear/` - Clear conversation messages
- `/message/send/` - Send message
- `/upload/` - Upload documents
- `/settings/` - Settings page
- `/library/clear/` - Clear document library

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by ChatGPT's interface
- Built with Django and HTMX
- Powered by Ollama and LangChain
- Uses ChromaDB for vector storage

## 📧 Support

If you encounter any issues or have questions, please check:
1. Ollama is running (`ollama serve`)
2. Required model is downloaded (`ollama pull llava:7b`)
3. All dependencies are installed
4. Database migrations are applied

---

**Enjoy your personal AI assistant with document-based knowledge! 🚀**
