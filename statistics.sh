#!/usr/bin/env bash
coverage run --source='.' manage.py test
echo "Coverage Report"
coverage html --omit='challange_jobandtalent/asgi.py,manage.py,wsgi.py'
