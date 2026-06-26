#!/usr/bin/env python3
"""
Диагностика подключения Seedance 2.0 / 2.0 mini к Volcengine / BytePlus Ark.

«Двухсекундная интеграция»: с ключом из .env дёргает обе модели и говорит,
подключены они или нет. Точно различает:
  • неверный/просроченный ключ        (401/403)
  • модель не активирована в аккаунте (model not found / access denied)
  • модель подключена                 (задача принята → вернулся task_id)

Запуск (на сервере, где есть .env):
    cd /opt/avsound/mcp-server
    venv/bin/python check_connection.py
Локально:
    ARK_API_KEY=... python3 check_connection.py

По умолчанию НЕ ждёт готовое видео (генерация платная/долгая) — достаточно,
что Ark принял задачу. Это подтверждает: ключ валиден и модель подключена.
"""
import os
import sys
import asyncio
import httpx
import seedance


async def probe(alias: str) -> bool:
    model_id = seedance.resolve_model(alias)
    print(f"\n▶ {alias:5} → {model_id}")
    try:
        task = await seedance.create_task(
            prompt="test connection",
            resolution="480p",
            duration=5,
            model=alias,
        )
    except httpx.HTTPStatusError as e:
        code = e.response.status_code
        body = e.response.text
        if code in (401, 403):
            print(f"  ❌ Ключ отклонён ({code}). Проверь ARK_API_KEY. {body}")
        elif "not found" in body.lower() or "not open" in body.lower() or "access" in body.lower():
            print(f"  ❌ Модель НЕ подключена в аккаунте ({code}). Активируй её в консоли Ark.\n     {body}")
        else:
            print(f"  ❌ Ошибка Ark ({code}): {body}")
        return False
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")
        return False

    task_id = task.get("id", "")
    print(f"  ✅ Подключена. Задача принята: task_id={task_id}")
    return True


async def main() -> int:
    if not os.environ.get("ARK_API_KEY", "").strip():
        print("❌ ARK_API_KEY не задан (в .env или окружении). Нечего проверять.")
        return 2
    print(f"Base URL: {seedance.ARK_BASE_URL}")
    results = [await probe("2.0"), await probe("mini")]
    ok = all(results)
    print("\n" + ("✅ Обе модели подключены." if ok else "⚠️  Есть проблемы — см. выше."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
