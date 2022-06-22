from datetime import datetime
import time
from typing import List

from core.broker.celery import celery_app
from deps import get_db
import schemas.message as schema
from core.broker.redis import redis
import crud.message as crud
import asyncio


@celery_app.task(name="queue.test")
def test():
    print(datetime.now())


@celery_app.task(name="queue.schedule_dispatcher")
def schedule_dispatcher():
    asyncio.run(check_nearest_messages())


async def check_nearest_messages():
    db = next(get_db())
    await redis.publish(f'thread', 'Started daemon of capturing scheduled messages')
    while True:
        messages: List[schema.MessageWithDate] = crud.get_nearest_messages(db)
        await redis.publish(f'thread', f'Tried to receive scheduled messages {messages}')
        for message in messages:
            message_date = datetime.strptime(message.created_date, "%Y-%m-%d %H:%M:%S")
            current_date = datetime.now()
            delta = message_date - current_date
            minutes = delta.seconds / 60
            await redis.publish(f'thread', minutes)
            await redis.publish(f'thread', message.toJSON())
            if minutes < 1:
                crud.make_message_sendable(db=db, message=message)
                await redis.publish(f'chat-{message.chat_id}', message.toJSON())
        time.sleep(30)