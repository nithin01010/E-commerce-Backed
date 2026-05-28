1. Concurancy = Row level locking for while ordering  , with_for_updates
2. Cache = ttl and write through
3. N + 1 queries = selectinload , we load tables required at the same time
4. Slow Query = Indexing
5. Security = Rate Limiting: FastAPI_limiter, tokens: secure = True # still need to add 
6. Celery
7. PgBouncer
8. Pagination = Cursor based