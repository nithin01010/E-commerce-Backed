To start backend: uvicorn app.main:app --reload
to start redis: sudo service redis-server start
to start celery: celery -A app.core.celery_app worker --loglevel=info -P gevent