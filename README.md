# 🚀 StackIt — Stack Overflow Clone

A full-featured Q&A platform built with Django, PostgreSQL, and vanilla JavaScript.

---

## Features

- **User Auth** — Register, login, logout, remember me, profile pages
- **Questions** — Ask, edit, delete, search, filter, tag, bookmark
- **Answers** — Post, edit, delete, mark as accepted
- **Comments** — On both questions and answers (AJAX)
- **Voting** — Up/downvote questions and answers (AJAX, no page reload)
- **Reputation System** — Automatic point tracking (+5/+10/+15/-2)
- **Badge System** — Bronze/silver/gold badges awarded automatically
- **Tag System** — Create, browse, filter questions by tag
- **Notifications** — Real-time bell, unread count, mark all read
- **Bookmarks** — Save/unsave questions
- **Reports** — Report spam, abuse, duplicates
- **Dark Mode** — Per-user toggle persisted to profile
- **Search** — Full-text across titles, content, tags
- **Admin Panel** — Custom Django admin with moderation tools
- **Responsive** — Desktop, tablet, mobile layouts
- **Rich Editor** — Markdown toolbar with live preview

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Database | PostgreSQL |
| Frontend | HTML5, CSS3, Vanilla JS (no frameworks) |
| Auth | Django built-in auth |
| ORM | Django ORM |
| Templates | Django Templates |
| Styling | Custom CSS (no Bootstrap) |

---

## Project Structure

```
stackit/
├── accounts/          # User auth, profiles, reputation
├── answers/           # Answer CRUD and acceptance
├── badges/            # Badge definitions and auto-awarding
├── comments/          # Generic comments (question + answer)
├── notifications/     # Notification system + context processor
├── questions/         # Question CRUD, search, bookmarks
├── reports/           # Content reporting
├── tags/              # Tag management
├── votes/             # Generic voting system
├── stackit/           # Project settings, urls, wsgi
├── templates/         # All HTML templates
├── static/
│   ├── css/style.css  # All styles (~700 lines custom CSS)
│   └── js/main.js     # Voting, comments, editor, dark mode JS
├── media/             # User uploads (avatars, images)
├── requirements.txt
└── README.md
```

---

## Quick Start (PostgreSQL)

```bash
# 1. Clone / extract the project
cd stackit

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create PostgreSQL database/user first
# See "PostgreSQL Setup" below, then export DB_* environment variables.

# 5. Run migrations
python manage.py migrate

# 6. Create default badges
python manage.py create_badges

# 7. Create a superuser
python manage.py createsuperuser

# 8. Start the server
python manage.py runserver
```

Visit http://127.0.0.1:8000

---

## PostgreSQL Setup

### 1. Create database and user

```sql
-- In psql
CREATE DATABASE stackit_db;
CREATE USER stackit_user WITH ENCRYPTED PASSWORD 'stackit_password';
GRANT ALL PRIVILEGES ON DATABASE stackit_db TO stackit_user;
ALTER DATABASE stackit_db OWNER TO stackit_user;
```

### 2. Configure environment variables

```bash
export DB_NAME=stackit_db
export DB_USER=stackit_user
export DB_PASSWORD=stackit_password
export DB_HOST=localhost
export DB_PORT=5432
export DJANGO_SECRET_KEY=your-secret-key-here
```

Or create a `.env` file and load it:

```bash
DB_NAME=stackit_db
DB_USER=stackit_user
DB_PASSWORD=stackit_password
DB_HOST=localhost
DB_PORT=5432
DJANGO_SECRET_KEY=replace-with-50-char-random-string
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. Run with PostgreSQL

```bash
python manage.py migrate
python manage.py create_badges
python manage.py createsuperuser
python manage.py runserver
```

---

## Reputation Points

| Action | Points |
|--------|--------|
| Question upvoted | +5 |
| Answer upvoted | +10 |
| Answer accepted | +15 |
| Question downvoted | −2 |
| Answer downvoted | −2 |

---

## Badge Tiers

**Bronze** — First Question, First Answer, Curious, Teacher  
**Silver** — 100 Reputation, Prolific Questioner, Top Answerer, Good Question  
**Gold** — 1000 Reputation, Great Answer, Legend  

---

## Admin Panel

Visit `/admin/` with your superuser credentials.

- Manage users, questions, answers, tags, badges, reports
- Resolve/dismiss reports via bulk actions
- View reputation history per user

---

## API / URL Routes

| URL | View |
|-----|------|
| `/` | Home (question feed) |
| `/ask/` | Ask a question |
| `/questions/<slug>/` | Question detail |
| `/accounts/register/` | Sign up |
| `/accounts/login/` | Log in |
| `/accounts/profile/<username>/` | User profile |
| `/accounts/users/` | User directory |
| `/tags/` | Tag browser |
| `/tags/<slug>/` | Questions by tag |
| `/badges/` | Badge list |
| `/notifications/` | Notification inbox |
| `/saved/` | Bookmarked questions |
| `/search/?q=...` | Search |
| `/votes/<type>/<id>/<value>/` | Vote (AJAX) |
| `/admin/` | Admin dashboard |

---

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Configure PostgreSQL `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`
- [ ] Run `python manage.py collectstatic`
- [ ] Serve media files via nginx/S3
- [ ] Set up HTTPS
- [ ] Configure `EMAIL_BACKEND` for real email
- [ ] Use gunicorn/uwsgi behind nginx

```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

---

## Load Sample Data (optional)

```python
# In Django shell: python manage.py shell
from django.contrib.auth.models import User
from questions.models import Question
from tags.models import Tag
from django.utils.text import slugify

users = [User.objects.create_user(f'dev{i}', f'dev{i}@example.com', 'Pass1234') for i in range(5)]
tags = [Tag.objects.get_or_create(name=n, slug=slugify(n))[0] for n in ['python','django','javascript','css','postgresql']]

questions = [
    "How do I reverse a list in Python?",
    "What is the difference between == and === in JavaScript?",
    "How to use Django ORM for complex queries?",
    "Best practices for CSS Flexbox layouts?",
    "How to set up PostgreSQL on Ubuntu?",
]
for i, title in enumerate(questions):
    q = Question.objects.create(title=title, content=f"Detailed question about {title.lower()} with code examples and what I've tried so far.", author=users[i])
    q.tags.add(tags[i])
print("Sample data created!")
```
