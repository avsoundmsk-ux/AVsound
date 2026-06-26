#!/usr/bin/env python3
"""
Seedance 2 — генерация видео через официальный Volcengine / BytePlus Ark API.

Поставщик: ByteDance Ark (ModelArk). Поддерживает text-to-video (t2v) и
image-to-video (i2v). Генерация асинхронная: создаём задачу → опрашиваем статус →
получаем ссылку на готовое видео.

Конфигурация через переменные окружения (.env):
  ARK_API_KEY     — ключ доступа Ark (обязателен для генерации)
  ARK_BASE_URL    — базовый URL API. По умолчанию Volcengine (Пекин):
                    https://ark.cn-beijing.volces.com/api/v3
                    Для BytePlus (международный): https://ark.ap-southeast.bytepluses.com/api/v3
  SEEDANCE_MODEL  — ID модели/эндпоинта Seedance 2 из консоли Ark
                    (например seedance-2-0 или ep-xxxxxxxx)
"""
import os
import asyncio
import httpx

ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
SEEDANCE_MODEL = os.environ.get("SEEDANCE_MODEL", "seedance-2-0")

# Статусы задачи в Ark
_DONE = "succeeded"
_FAILED = {"failed", "cancelled"}


def _api_key() -> str:
    key = os.environ.get("ARK_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ARK_API_KEY не задан. Впиши ключ Volcengine/BytePlus Ark в .env "
            "и перезапусти сервис (systemctl restart avsound-mcp)."
        )
    return key


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }


def _build_prompt(prompt: str, resolution: str, ratio: str, duration: int) -> str:
    """Параметры Seedance передаются суффиксами команды в тексте промпта."""
    parts = [prompt.strip()]
    if resolution:
        parts.append(f"--resolution {resolution}")
    if ratio:
        parts.append(f"--ratio {ratio}")
    if duration:
        parts.append(f"--duration {duration}")
    return " ".join(parts)


async def create_task(
    prompt: str,
    image_url: str = "",
    resolution: str = "1080p",
    ratio: str = "16:9",
    duration: int = 5,
    model: str = "",
) -> dict:
    """
    Создать задачу генерации видео.
    Если задан image_url — режим image-to-video, иначе text-to-video.
    Возвращает словарь ответа Ark (содержит id задачи).
    """
    content = [{"type": "text", "text": _build_prompt(prompt, resolution, ratio, duration)}]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    payload = {"model": model or SEEDANCE_MODEL, "content": content}

    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{ARK_BASE_URL}/contents/generations/tasks",
            headers=_headers(),
            json=payload,
        )
        r.raise_for_status()
        return r.json()


async def get_task(task_id: str) -> dict:
    """Получить текущее состояние задачи генерации."""
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(
            f"{ARK_BASE_URL}/contents/generations/tasks/{task_id}",
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()


def _video_url(task: dict) -> str:
    content = task.get("content") or {}
    return content.get("video_url", "")


async def wait_for_task(task_id: str, timeout: int = 600, interval: int = 10) -> dict:
    """
    Опрашивать задачу пока не завершится (succeeded/failed) или не выйдет timeout.
    Возвращает финальное (или последнее) состояние задачи.
    """
    waited = 0
    task = await get_task(task_id)
    while task.get("status") not in (_DONE, *_FAILED):
        if waited >= timeout:
            break
        await asyncio.sleep(interval)
        waited += interval
        task = await get_task(task_id)
    return task
