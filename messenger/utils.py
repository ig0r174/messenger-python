from aiohttp import ClientSession, ClientTimeout


async def async_query(task_url: str, timeout: int = 5, **kwargs):
    """Выполняет post-запрос во внутренний rest api сервис
    
    Args:
        task_url: ссылка на endpoint
        timeout: таймаут запроса
        **kwargs: параметры тела запроса
    """
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(timeout=timeout) as session:
        async with session.post(task_url, json=kwargs) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception
    return result
