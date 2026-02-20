# 🚀 Quick Reference Card

## Essential Commands

### Start the Application
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Django (if not running)
python manage.py runserver

# Browser
http://127.0.0.1:8000/
```

### First Time Setup
```bash
# Use the automated script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
ollama pull llava:7b
ollama pull nomic-embed-text
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `Cmd/Ctrl + R` | Refresh page |

---

## UI Navigation

### Main Interface
- **New Chat**: Click "+ New Chat" button (top left)
- **Settings**: Click ⚙️ icon (top right)
- **Sidebar Toggle**: Click ☰ icon (mobile)

### Conversation Actions (3-dot menu)
- **Rename**: Change conversation title
- **Clear**: Remove all messages
- **Delete**: Remove entire conversation

---

## Common Tasks

### Start a New Chat
1. Click "+ New Chat"
2. Type your message
3. Press Enter

### Upload Documents
1. Click Settings (⚙️)
2. Choose files (PDF/TXT)
3. Click "Upload & Process"
4. Wait for confirmation

### Ask About Documents
1. Upload documents first
2. Return to chat
3. Ask questions about the content
4. Get AI responses based on your docs

---

## File Locations

| Item | Location |
|------|----------|
| Uploaded docs | `books/` |
| Vector DB | `book_db/` |
| SQLite DB | `db.sqlite3` |
| Static files | `chat/static/chat/` |
| Templates | `chat/templates/chat/` |

---

## Troubleshooting Quick Fixes

### "Connection Refused" Error
```bash
ollama serve
```

### "Model Not Found" Error
```bash
ollama pull llava:7b
```

### Database Issues
```bash
python manage.py migrate
```

### Reset Everything
```bash
rm db.sqlite3
rm -rf book_db/
python manage.py migrate
```

---

## URLs Reference

| URL | Purpose |
|-----|---------|
| `/` | Main chat |
| `/settings/` | Settings page |
| `/admin/` | Django admin |

---

## Configuration Files

### Change AI Model
File: `chat/ai_service.py`
```python
DEFAULT_LLM_MODEL = "llava:7b"  # Change here
```

### Adjust Chunk Size
File: `chat/ai_service.py`
```python
chunk_size=600,  # Adjust here
chunk_overlap=120,
```

### Debug Mode
File: `chatgpt_clone/settings.py`
```python
DEBUG = True  # Set to False for production
```

---

## Port Configuration

### Default Port
```bash
python manage.py runserver  # Port 8000
```

### Custom Port
```bash
python manage.py runserver 8001
```

### Ollama Port
```
Default: http://localhost:11434
```

---

## Database Commands

### Create Superuser
```bash
python manage.py createsuperuser
```

### Access Admin
```
http://127.0.0.1:8000/admin/
```

### Shell Access
```bash
python manage.py shell
```

### Check Conversations
```python
from chat.models import Conversation, Message
Conversation.objects.all()
Message.objects.all()
```

---

## Ollama Commands

### List Models
```bash
ollama list
```

### Pull Model
```bash
ollama pull <model-name>
```

### Test Model
```bash
ollama run llava:7b "Hello!"
```

### Remove Model
```bash
ollama rm <model-name>
```

---

## Development Commands

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Create App
```bash
python manage.py startapp <app-name>
```

---

## Environment Variables (Optional)

Create `.env` file:
```bash
DEBUG=True
SECRET_KEY=your-secret-key
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llava:7b
```

---

## Dependencies

### Core
- Django 5.x
- langchain
- langchain-community
- langchain-chroma
- langchain-ollama

### AI/ML
- chromadb
- pypdf
- tqdm

### Install All
```bash
pip install -r requirements.txt
```

---

## Project Structure (Quick View)

```
Website/
├── chat/              # Main app
├── chatgpt_clone/     # Project settings
├── books/             # Uploaded docs
├── book_db/           # Vector DB
├── db.sqlite3         # Database
├── manage.py          # Django CLI
└── requirements.txt   # Dependencies
```

---

## Status Indicators

### Server Running
```
Starting development server at http://127.0.0.1:8000/
```

### Ollama Running
```bash
curl http://localhost:11434/api/tags
# Should return JSON
```

### Database Ready
```bash
python manage.py showmigrations
# All should have [X]
```

---

## Performance Tips

### Faster Responses
- Use smaller model: `ollama pull llama2:7b`
- Reduce chunk retrieval: `k=4` instead of `k=8`
- Smaller chunk size: `chunk_size=400`

### Better Accuracy
- Use larger model: `ollama pull llama2:13b`
- More chunks: `k=10`
- Larger overlap: `chunk_overlap=150`

---

## Security Checklist (Production)

- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up HTTPS
- [ ] Add user authentication
- [ ] Configure CORS properly
- [ ] Use environment variables

---

## Useful Links

- **Ollama**: https://ollama.ai/
- **Django Docs**: https://docs.djangoproject.com/
- **LangChain**: https://python.langchain.com/
- **HTMX**: https://htmx.org/

---

## Support Files

- `README.md` - Full documentation
- `FEATURES.md` - Feature list
- `TROUBLESHOOTING.md` - Problem solving
- `ARCHITECTURE.md` - System design
- `SUMMARY.md` - Project completion

---

**Keep this card handy for quick reference!** 📌
