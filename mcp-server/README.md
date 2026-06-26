# AVsound MCP Server — Установка на Hetzner

## Что это

MCP сервер который даёт любому Claude доступ к базе знаний AVsound (GitHub).

## Установка на Hetzner (одна команда)

```bash
wget -O - https://raw.githubusercontent.com/avsoundmsk-ux/avsound/main/mcp-server/install.sh | bash
```

После установки заполни токен:
```bash
nano /opt/avsound/mcp-server/.env
# Вставь GITHUB_TOKEN=ghp_...
systemctl restart avsound-mcp
```

## Подключение к Claude Code

Добавь в `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "avsound-knowledge": {
      "url": "http://ВАШ_HETZNER_IP:8080/sse"
    }
  }
}
```

После этого любая сессия Claude Code будет иметь инструменты:
- `remember` — запомнить что-то
- `add_client` — добавить клиента
- `search_knowledge` — найти информацию
- `list_knowledge` — показать список
- `read_knowledge` — прочитать запись
- `generate_video` — сгенерировать видео через Seedance 2.0 (t2v / i2v / v2v)
- `check_video` — проверить статус и получить ссылку на готовое видео

## Seedance 2.0 — генерация видео

Поставщик — официальный **Volcengine / BytePlus Ark** (ByteDance ModelArk).
Подключены **две модели**: Seedance 2.0 (`model="2.0"`) и Seedance 2.0 mini
(`model="mini"`). Режимы: text-to-video, image-to-video и **video-to-video**.
Генерация асинхронная: `generate_video` создаёт задачу, `check_video` опрашивает
статус и отдаёт ссылку.

Настрой ключ и модели в `.env` (см. `.env.example`):

```bash
ARK_API_KEY=...                                   # ключ из консоли Ark
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3   # или BytePlus ap-southeast
SEEDANCE_MODEL=seedance-2-0                        # ID эндпоинта Seedance 2.0
SEEDANCE_MODEL_MINI=seedance-2-0-mini             # ID эндпоинта Seedance 2.0 mini
systemctl restart avsound-mcp
```

Где взять: консоль Volcengine Ark (https://console.volcengine.com/ark) или
BytePlus ModelArk → создать API Key и эндпоинты обеих моделей Seedance 2.0.

Пример вызова:
- video-to-video (Seedance 2.0): `generate_video("добавь дым и лучи света", video_url="https://...mp4", model="2.0")`
- video-to-video (mini): `generate_video("стилизуй под неон", video_url="https://...mp4", model="mini")`
- image-to-video: `generate_video("камера медленно наезжает", image_url="https://...jpg")`
- text-to-video: `generate_video("концертная сцена, дым, лучи света", resolution="1080p", duration=5)`
- затем: `check_video("<task_id>")` → ссылка на видео

## Obsidian синхронизация

1. Установи плагин **obsidian-git** в Obsidian
2. Открой vault как папку `knowledge/` из этого репозитория
3. Настрой автопуш каждые 5 минут

Тогда всё что Claude сохраняет — сразу появляется в Obsidian и наоборот.

## Получить GitHub Token

https://github.com/settings/tokens → New token → выбери `repo` scope
