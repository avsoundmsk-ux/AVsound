#!/usr/bin/env python3
"""
Seedance 2 — генерация видео через официальный Volcengine / BytePlus Ark API.

Поставщик: ByteDance Ark (ModelArk). Поддерживает text-to-video (t2v),
image-to-video (i2v) и video-to-video (v2v). Две модели: Seedance 2.0 и
Seedance 2.0 mini. Генерация асинхронная: создаём задачу → опрашиваем статус →
получаем ссылку на готовое видео.

Конфигурация через переменные окружения (.env):
  ARK_API_KEY          — ключ доступа Ark (обязателен для генерации)
  ARK_BASE_URL         — базовый URL API. По умолчанию Volcengine (Пекин):
                         https://ark.cn-beijing.volces.com/api/v3
                         BytePlus (международный): https://ark.ap-southeast.bytepluses.com/api/v3
  SEEDANCE_MODEL       — ID модели/эндпоинта Seedance 2.0 из консоли Ark
                         (например seedance-2-0 или ep-xxxxxxxx)
  SEEDANCE_MODEL_MINI  — ID модели/эндпоинта Seedance 2.0 mini
                         (например seedance-2-0-mini или ep-xxxxxxxx)
"""
import os
import asyncio
import httpx

ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")

# Две модели Seedance 2.0. Ключ алиаса -> ID модели/эндпоинта Ark.
# Дефолты — официальные ID Volcengine Ark (на BytePlus префикс dreamina- вместо doubao-).
MODELS = {
    "2.0": os.environ.get("SEEDANCE_MODEL", "doubao-seedance-2-0-260128"),
    "mini": os.environ.get("SEEDANCE_MODEL_MINI", "doubao-seedance-2-0-mini-260615"),
}
DEFAULT_MODEL = "2.0"

# Принимаемые написания алиасов -> канонический ключ MODELS
_ALIASES = {
    "2.0": "2.0", "2": "2.0", "full": "2.0", "pro": "2.0", "seedance-2-0": "2.0",
    "mini": "mini", "2.0-mini": "mini", "2.0 mini": "mini",
    "2-mini": "mini", "seedance-2-0-mini": "mini",
}

# Статусы задачи в Ark
_DONE = "succeeded"
_FAILED = {"failed", "cancelled"}


def resolve_model(model: str = "") -> str:
    """Алиас модели ('2.0' | 'mini' и варианты) -> реальный ID для Ark."""
    if not model:
        return MODELS[DEFAULT_MODEL]
    key = _ALIASES.get(model.strip().lower())
    if key is None:
        # Не алиас — считаем, что передан готовый ID модели/эндпоинта.
        return model
    return MODELS[key]


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
    video_url: str = "",
    resolution: str = "1080p",
    ratio: str = "16:9",
    duration: int = 5,
    model: str = "",
) -> dict:
    """
    Создать задачу генерации видео.
    Режим определяется входом: video_url -> video-to-video,
    image_url -> image-to-video, иначе text-to-video.
    model: алиас '2.0' | 'mini' (или готовый ID эндпоинта Ark).
    Возвращает словарь ответа Ark (содержит id задачи).
    """
    content = [{"type": "text", "text": _build_prompt(prompt, resolution, ratio, duration)}]
    if video_url:
        content.append({"type": "video_url", "video_url": {"url": video_url}})
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    payload = {"model": resolve_model(model), "content": content}

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
