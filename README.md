# consolidation

project_name = "IndieGo News App"
dockerhub_url = "https://hub.docker.com/r/cmerkle1/capstone"

## Overview

A Django-based news publishing platform with support for:
- Custom user roles (reader, journalist, editor)
- Article approval workflow
- Subscriptions to publishers or journalists
- REST API with session authentication
- Docker and venv support

## Setup (venv)

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
