# 🚀 StackIt – Stack Overflow Clone

A simple Q&A web application built with Django, PostgreSQL, HTML, CSS, and JavaScript. Users can ask questions, post answers, vote, comment, and manage their profiles.

## Features

* User registration and login
* Ask, edit, and delete questions
* Post, edit, and delete answers
* Upvote and downvote questions and answers
* Comment on questions and answers
* Search questions by title
* Tags and bookmarks
* User profiles
* Responsive design

## Tech Stack

* Django
* PostgreSQL
* HTML
* CSS
* JavaScript

## Installation

```bash
git clone <repository-url>
cd stackit

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000
```

## Project Structure

```
stackit/
├── accounts/
├── questions/
├── answers/
├── comments/
├── votes/
├── tags/
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```

## Author

Developed as a learning project using Django.
