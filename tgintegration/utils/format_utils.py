from typing import Any, Optional


def truncate(text: str, maxlen: Optional[int] = 50):
    if maxlen and len(text) > maxlen:
        text = text[: maxlen - 3] + "..."
    return text


def display_name(entity: Any, prefer_username: bool = True) -> str:
    if prefer_username and (username := getattr(entity, "username", None)):
        # noinspection PyUnboundLocalVariable
        return f"@{username.lstrip('@')}"
    if title := getattr(entity, "title", None):
        return truncate(title)
    if first_name := getattr(entity, "first_name", None):
        if last_name := getattr(entity, "last_name", None):
            return truncate(f"{first_name} {last_name}")
        return truncate(entity.first_name)
    raise ValueError(f"The entity of type {type(entity)} does not seem to have a display name.")
