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

## Obsidian синхронизация

1. Установи плагин **obsidian-git** в Obsidian
2. Открой vault как папку `knowledge/` из этого репозитория
3. Настрой автопуш каждые 5 минут

Тогда всё что Claude сохраняет — сразу появляется в Obsidian и наоборот.

## Получить GitHub Token

https://github.com/settings/tokens → New token → выбери `repo` scope
