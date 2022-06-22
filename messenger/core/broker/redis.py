from os import getenv

from redis import asyncio as aioredis


redis = aioredis.from_url(f"redis://redis:{getenv('REDIS_PORT', 6379)}")
