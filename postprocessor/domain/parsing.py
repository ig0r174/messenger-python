import re

from schemas import Extra


def get_links(text: str):
    """Находит ссылки в тексте"""
    pattern = r'(https?://[^\s]+)'
    links = re.findall(pattern, text)

    result = []
    for link in links:
        result.append(
            Extra(text=link, offset=text.find(link), length=len(link), type='link')
        )

    return result


def get_hashtags(text: str):
    """Находит хэштеги в тексте"""
    pattern = r'(\B(\#[a-zA-Z]+\b)(?!;))'
    hashtags = re.findall(pattern, text)

    result = []
    for hashtag, _ in hashtags:
        result.append(
            Extra(text=hashtag, offset=text.find(hashtag), length=len(hashtag), type='hashtag')
        )

    return result


def get_mentions(text: str):
    """Находит упоминания в тексте"""
    pattern = r'(\B(\@[a-zA-Z1-9]+\b)(?!;))'
    mentions = re.findall(pattern, text)

    result = []
    for mention, _ in mentions:
        result.append(
            Extra(text=mention, offset=text.find(mention), length=len(mention), type='mention')
        )

    return result


def get_extra(text: str):
    """Находит в тексте экстра-данные: ссылки, упоминания и т.д."""
    extra = []

    extra += get_links(text)
    extra += get_hashtags(text)
    extra += get_mentions(text)

    return extra
