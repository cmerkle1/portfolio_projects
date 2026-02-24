# Sticky Notes Django Project

## Overview
A web-based sticky notes CRUD app built with Django. Users can create, update, and manage notes across sessions.

## Features
- Create, read, edit, and delete sticky notes
- Responsive frontend, themed like a post-it note board

## Required Packages
- asgiref: required by Django to support server communication
- Django: the main web framework used to build this project
- sqlparse: parser used for formatting and parsing SQL queries
- tzdata: provides time zone database information


## Setup Instructions

1. **Clone the repository**
git clone https://github.com/cmerkle1/portfolio_projects
cd sticky_notes

2.  **Set up virtual environment**
python -m venv venv

3. **Activate (Windows PowerShell)**
.\venv\Scripts\Activate.ps1

4. **Install dependencies**
pip install -r requirements.txt

5. **Run migrations and start server**
python manage.py migrate
python manage.py runserver
open web browser and access 127.0.0.1:8000