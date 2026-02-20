# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. ❌ Connection Refused Error (Errno 61)

**Error Message:**
```
I encountered an error while processing your request: [Errno 61] Connection refused
```

**Cause:** Ollama is not running on your system.

**Solution:**
```bash
# Start Ollama in a new terminal
ollama serve
```

**Verify it's running:**
```bash
# Check if Ollama is responding
curl http://localhost:11434/api/tags

# Or list available models
ollama list
```

---

### 2. ❌ Model Not Found

**Error Message:**
```
Error: model 'llava:7b' not found
```

**Solution:**
```bash
# Download the required model
ollama pull llava:7b

# Or use a different model
ollama pull llama2
```

**To change the model in the app:**
Edit `chat/ai_service.py`:
```python
DEFAULT_LLM_MODEL = "llama2"  # Change to your model
```

---

### 3. ❌ Import Errors (Missing Dependencies)

**Error Message:**
```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### 4. ❌ Database Errors

**Error Message:**
```
django.db.utils.OperationalError: no such table: chat_conversation
```

**Solution:**
```bash
# Run migrations
python manage.py migrate

# If issues persist, delete db and recreate
rm db.sqlite3
python manage.py migrate
```

---

### 5. ❌ Static Files Not Loading

**Symptoms:** No CSS styling, broken layout

**Solution:**
```bash
# Collect static files (for production)
python manage.py collectstatic

# For development, make sure DEBUG=True in settings.py
```

---

### 6. ❌ Document Upload Not Working

**Symptoms:** Files upload but no processing happens

**Checklist:**
1. ✅ Ollama is running (`ollama serve`)
2. ✅ Embedding model is available (`ollama pull nomic-embed-text`)
3. ✅ Check terminal for error messages
4. ✅ Verify file format (PDF or TXT only)

**Solution:**
```bash
# Pull the embedding model
ollama pull nomic-embed-text

# Check if books directory exists
ls -la books/

# Check if vector DB is being created
ls -la book_db/
```

---

### 7. ❌ Port Already in Use

**Error Message:**
```
Error: That port is already in use.
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
python manage.py runserver 8001
```

---

### 8. ❌ Slow Response Times

**Symptoms:** AI takes a long time to respond

**Causes & Solutions:**

1. **Large documents:** Reduce chunk size in `ai_service.py`
   ```python
   chunk_size=400,  # Reduce from 600
   ```

2. **Too many chunks retrieved:** Reduce k value
   ```python
   docs = db.similarity_search_with_score(query, k=4)  # Reduce from 8
   ```

3. **Slow model:** Use a smaller/faster model
   ```bash
   ollama pull llama2:7b  # Smaller than llava
   ```

---

### 9. ❌ Conversation Actions Not Working

**Symptoms:** Rename, clear, delete buttons don't work

**Checklist:**
1. ✅ JavaScript is enabled in browser
2. ✅ Check browser console for errors (F12)
3. ✅ CSRF token is present in forms

**Solution:**
```bash
# Hard refresh the page
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

# Clear browser cache
# Then restart the server
```

---

### 10. ❌ HTMX Not Working

**Symptoms:** Page reloads instead of dynamic updates

**Solution:**
1. Check if HTMX is loaded (view page source)
2. Verify HTMX CDN is accessible
3. Check browser console for JavaScript errors

**Alternative:** Download HTMX locally
```bash
# Download HTMX
curl -o chat/static/chat/js/htmx.min.js https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js
```

Update `index.html`:
```html
<script src="{% static 'chat/js/htmx.min.js' %}"></script>
```

---

## 🔍 Debugging Tips

### Enable Debug Mode
In `settings.py`:
```python
DEBUG = True
```

### Check Server Logs
Watch the terminal where `manage.py runserver` is running for error messages.

### Check Browser Console
Press F12 and look for JavaScript errors in the Console tab.

### Test Ollama Directly
```bash
# Test if Ollama is working
ollama run llava:7b "Hello, how are you?"
```

### Check Database
```bash
# Open Django shell
python manage.py shell

# Check conversations
from chat.models import Conversation, Message
print(Conversation.objects.all())
print(Message.objects.all())
```

---

## 📞 Still Having Issues?

### Quick Checklist
- [ ] Ollama is installed and running
- [ ] Required model is downloaded
- [ ] Virtual environment is activated
- [ ] Dependencies are installed
- [ ] Database migrations are applied
- [ ] Port 8000 is available
- [ ] Browser JavaScript is enabled

### Reset Everything
```bash
# Stop the server (Ctrl+C)

# Remove database and vector DB
rm db.sqlite3
rm -rf book_db/

# Reinstall dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Restart Ollama
ollama serve

# Start server
python manage.py runserver
```

---

## 🎯 Quick Start (From Scratch)

```bash
# 1. Install Ollama
# Visit: https://ollama.ai/

# 2. Start Ollama
ollama serve

# 3. Download model (in new terminal)
ollama pull llava:7b
ollama pull nomic-embed-text

# 4. Setup Python environment
cd Website
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Setup database
python manage.py migrate

# 7. Start server
python manage.py runserver

# 8. Open browser
# Navigate to: http://127.0.0.1:8000/
```

---

**Need more help?** Check the README.md and FEATURES.md files for detailed documentation.
