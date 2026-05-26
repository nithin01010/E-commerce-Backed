1. Concurancy = Row level locking for while ordering 
2. Cache = ttl and write through
3. N + 1 queries = selectload , we load tables required at the same time
4. Slow Query = Indexing
5. Security = Rate Limiting- FastAPI_limiter, tokens - secure = True