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
- `generate_video` — сгенерировать видео через Seedance 2 (t2v / i2v)
- `check_video` — проверить статус и получить ссылку на готовое видео

## Seedance 2 — генерация видео

Поставщик — официальный **Volcengine / BytePlus Ark** (ByteDance ModelArk).
Поддерживаются text-to-video и image-to-video. Генерация асинхронная:
`generate_video` создаёт задачу, `check_video` опрашивает статус и отдаёт ссылку.

Настрой ключ в `.env` (см. `.env.example`):

```bash
ARK_API_KEY=...                                   # ключ из консоли Ark
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3   # или BytePlus ap-southeast
SEEDANCE_MODEL=seedance-2-0                        # ID модели/эндпоинта Seedance 2
systemctl restart avsound-mcp
```

Где взять: консоль Volcengine Ark (https://console.volcengine.com/ark) или
BytePlus ModelArk → создать API Key и эндпоинт модели Seedance 2.

Пример вызова:
- text-to-video: `generate_video("концертная сцена, дым, лучи света", resolution="1080p", ratio="16:9", duration=5)`
- image-to-video: `generate_video("камера медленно наезжает", image_url="https://...jpg")`
- затем: `check_video("<task_id>")` → ссылка на видео

## Obsidian синхронизация

1. Установи плагин **obsidian-git** в Obsidian
2. Открой vault как папку `knowledge/` из этого репозитория
3. Настрой автопуш каждые 5 минут

Тогда всё что Claude сохраняет — сразу появляется в Obsidian и наоборот.

## Получить GitHub Token

https://github.com/settings/tokens → New token → выбери `repo` scope
