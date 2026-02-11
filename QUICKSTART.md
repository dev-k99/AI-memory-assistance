# ⚡ Quick Start Guide

Get AI Memory Assistant running in **5 minutes**!

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] PostgreSQL 15+ installed and running
- [ ] Groq API key ([Get free here](https://console.groq.com))

---

## 🚀 Installation (4 Commands)

### 1. Clone & Setup

```bash
git clone https://github.com/dev-k99/AI-memory-assistance.git
cd AI-memory-assistance
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
GROQ_API_KEY=your_groq_api_key_here
POSTGRES_PASSWORD=your_postgres_password_here
```

### 3. Initialize Database

```bash
python setup_database.py
```

### 4. Launch!

```bash
streamlit run app.py
```

**Open:** http://localhost:8501 

---

## ✅ Verify It's Working

### Test 1: Send a Message
```
You: Hello! My name is Sarah.
AI: Nice to meet you, Sarah!
```

**Check sidebar:** Should show "Messages in Memory: 2" ✅

### Test 2: Test Memory
```
You: What's my name?
AI: Your name is Sarah!
```

**SUCCESS!** The AI remembered! ✅

---

## 🐛 Quick Fixes

### "Database connection failed"
```bash
# Start PostgreSQL
pg_ctl start
# OR
brew services start postgresql  # macOS
```

### "Table not found"
```bash
python setup_database.py
```

### "Groq API error"
- Check your API key at [console.groq.com](https://console.groq.com)
- Verify you have credits

---

##  Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- See [CHANGELOG.md](CHANGELOG.md) for version history

---

**Need help?** Open an [issue](https://github.com/dev-k99/AI-memory-assistance/issues) on GitHub!