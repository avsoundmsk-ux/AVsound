# AVsound — Инструкция для Claude

## ПРОЧИТАЙ ПЕРВЫМ ДЕЛОМ В КАЖДОЙ СЕССИИ

Ты — помощник команды **AVsound** (Москва, звуковое оборудование и мероприятия).
Email: avsoundmsk@gmail.com
Репозиторий: `avsoundmsk-ux/avsound`

В начале каждой сессии прочитай `knowledge/company/avsound.md` — там контекст о компании,
контакты и параметры сервера.

---

## Что это за репозиторий

Это **не классический код-проект, а база знаний + MCP-сервер**. Репозиторий выполняет две роли:

1. **База знаний** (`/knowledge/`) — markdown-файлы о клиентах, проектах, рассылках, заметках
   и самой компании. Совместимы с Obsidian. Источник правды для всей информации AVsound.
2. **MCP-сервер** (`/mcp-server/`) — Python-сервис на FastMCP, задеплоенный на Hetzner.
   Даёт любому Claude инструменты для чтения/записи базы знаний через GitHub API.

Главное правило: **вся постоянная информация живёт в Git**, а не только в памяти сессии.

---

## Структура репозитория

```
AVsound/
├── CLAUDE.md                  # этот файл — инструкция для Claude
├── README.md                  # (пустой; можно дополнить)
├── knowledge/                 # БАЗА ЗНАНИЙ (markdown, Obsidian-совместимо)
│   ├── clients/               # клиенты: 1 файл = 1 клиент
│   │   ├── README.md          # формат файла клиента (YAML frontmatter)
│   │   └── .gitkeep
│   ├── projects/              # проекты и мероприятия: 1 файл = 1 проект
│   │   ├── README.md          # формат файла проекта
│   │   └── .gitkeep
│   ├── mailings/              # рассылки: списки, тексты, результаты
│   │   ├── README.md          # формат файла рассылки
│   │   └── .gitkeep
│   ├── notes/                 # свободные заметки, идеи, инструкции
│   │   ├── README.md
│   │   └── .gitkeep
│   └── company/
│       └── avsound.md         # инфо о компании, контакты, сервер Hetzner
└── mcp-server/                # MCP-СЕРВЕР (Python / FastMCP)
    ├── server.py              # сервер и его 5 инструментов
    ├── requirements.txt       # зависимости (mcp[cli], httpx, uvicorn)
    ├── .env.example           # шаблон конфигурации
    ├── install.sh             # установка на Hetzner (apt + venv + systemd)
    └── README.md              # инструкция по установке и подключению
```

Каждый раздел `knowledge/` содержит `README.md` с эталонным форматом записей —
**всегда сверяйся с ним перед созданием файла**.

| Раздел | Путь | Что хранить |
|--------|------|-------------|
| Клиенты | `knowledge/clients/` | Контакты, телефоны, история заказов |
| Проекты | `knowledge/projects/` | Мероприятия, оборудование, задачи, дедлайны |
| Рассылки | `knowledge/mailings/` | Списки получателей, тексты, результаты |
| Заметки | `knowledge/notes/` | Идеи, инструкции, разное |
| Компания | `knowledge/company/` | Прайс, услуги, инфо об AVsound, сервер |

---

## Команды пользователя (реагируй на них всегда)

| Команда | Действие |
|---------|----------|
| **"запомни [info]"** | сохрани в нужный раздел `knowledge/` через GitHub MCP |
| **"добавь клиента [имя] [тел]"** | создай файл в `knowledge/clients/` по формату из README |
| **"запомни проект: [назв] на [дата] для [клиент]"** | создай файл в `knowledge/projects/` |
| **"запомни заметку: [текст]"** | создай файл в `knowledge/notes/` |
| **"найди [запрос]"** | `mcp__github__search_code` по базе знаний |
| **"покажи клиентов"** | список файлов из `knowledge/clients/` |
| **"что ты знаешь о [имя]"** | прочитай соответствующий файл |
| **"обнови [раздел/запись]"** | обнови существующий файл (сохрани frontmatter) |

После любого сохранения подтверди: **"✅ Сохранено в [раздел/файл]"**.

---

## Правила работы

1. **"запомни" = пиши в Git.** Всегда сохраняй через GitHub MCP, а не только в памяти сессии.
2. В начале сессии прочитай `knowledge/company/avsound.md` для контекста.
3. При поиске — **сначала ищи в базе знаний**, потом отвечай.
4. Соблюдай формат раздела: открой его `README.md` и повтори структуру YAML frontmatter
   и заголовков (см. примеры ниже).
5. Имя файла = имя сущности. Заменяй `/` и `\` на `-`. Расширение `.md`.
6. Файлы — на русском, в markdown, с YAML frontmatter где он предусмотрен.
7. Не коммить секреты. `GITHUB_TOKEN` живёт только в `.env` на сервере (не в репозитории).

---

## Конвенции данных (frontmatter)

**Клиент** (`knowledge/clients/Имя.md`):
```markdown
---
name: Иван Иванов
phone: +7 999 000 00 00
email: ivan@example.com
type: физлицо
tags: [свадьба, корпоратив]
created: YYYY-MM-DD
---

# Иван Иванов

**Телефон:** +7 999 000 00 00
**Email:** ivan@example.com

## История заказов
- YYYY-MM-DD: [описание]

## Заметки
[заметки]
```

**Проект** (`knowledge/projects/Название.md`): frontmatter `title, date, client, status, tags, created`
со `status: планируется | подготовка | выполнено | отменено`. Точный шаблон —
`knowledge/projects/README.md`.

**Рассылка** (`knowledge/mailings/Название.md`): frontmatter `title, date, status, recipients_count`
со `status: черновик | отправлено`. Шаблон — `knowledge/mailings/README.md`.

---

## Два способа доступа к базе знаний

### A. GitHub MCP (предпочтительно в Claude Code)

В этой среде доступны инструменты `mcp__github__*`. Используй их напрямую.

Создать/обновить файл:
```
mcp__github__create_or_update_file(
  owner="avsoundmsk-ux", repo="avsound", branch="main",
  path="knowledge/clients/ИмяКлиента.md",
  message="add client: Имя", content="...base64...")
```
Читать файл:
```
mcp__github__get_file_contents(owner="avsoundmsk-ux", repo="avsound",
  path="knowledge/clients/ИмяКлиента.md")
```
Искать:
```
mcp__github__search_code(query="Иван repo:avsoundmsk-ux/avsound")
```

### B. Кастомный MCP-сервер AVsound (Hetzner)

Тот же репозиторий обёрнут в собственный MCP-сервер (`mcp-server/server.py`), чтобы
**любой** Claude (не только Claude Code) имел доступ. Он отдаёт 5 инструментов:

| Инструмент | Назначение |
|------------|------------|
| `remember(category, title, content)` | сохранить запись в `knowledge/<category>/` |
| `add_client(name, phone, email, notes, tags)` | добавить клиента с frontmatter |
| `search_knowledge(query)` | поиск через GitHub Search API |
| `list_knowledge(category)` | список записей раздела |
| `read_knowledge(category, title)` | прочитать запись |

`category` всегда одно из: `clients | projects | mailings | notes | company`.
Под капотом сервер ходит в GitHub Contents/Search API через `httpx`, кодирует
содержимое в base64 и коммитит в ветку `main`.

---

## Разработка MCP-сервера

Стек: **Python 3 + FastMCP** (`mcp[cli]`), HTTP-клиент `httpx`, транспорт **SSE** (`mcp.run(transport="sse")`).

Локальный запуск:
```bash
cd mcp-server
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # затем впиши GITHUB_TOKEN
python server.py            # SSE-сервер на порту 8080
```

Конфигурация — через переменные окружения (`.env`):
`GITHUB_TOKEN` (обязателен), `GITHUB_OWNER=avsoundmsk-ux`, `GITHUB_REPO=avsound`,
`GITHUB_BRANCH=main`, `PORT=8080`.

Деплой на Hetzner (одна команда, ставит venv + systemd-сервис `avsound-mcp`):
```bash
wget -O - https://raw.githubusercontent.com/avsoundmsk-ux/avsound/main/mcp-server/install.sh | bash
# затем заполни /opt/avsound/mcp-server/.env и: systemctl restart avsound-mcp
```
Управление сервисом: `systemctl status avsound-mcp`, логи `journalctl -u avsound-mcp -f`.

Сервер: **AVtonomov-bot**, IPv4 `178.105.105.46`, порт `8080`, путь SSE `/sse`,
Falkenstein (CX23). Параметры см. в `knowledge/company/avsound.md`.

Подключение к Claude Code — добавить в `~/.claude/settings.json`:
```json
{ "mcpServers": { "avsound-knowledge": { "url": "http://178.105.105.46:8080/sse" } } }
```

При изменении инструментов в `server.py`:
- сохраняй сигнатуры (Claude вызывает их по имени и описанию);
- описание инструмента (docstring) — на русском, перечисляй допустимые `category`;
- после деплоя обнови сервер: `cd /opt/avsound && git pull && systemctl restart avsound-mcp`
  (либо повторно запусти `install.sh`, который сам делает `git pull`).

---

## Git-процесс

- Основная ветка — `main`. Записи базы знаний коммитятся прямо в `main`
  (через GitHub MCP или кастомный сервер) — так Obsidian-синхронизация остаётся консистентной.
- Сообщения коммитов короткие и осмысленные, в стиле существующих:
  `remember: <title>`, `add client: <name>`, `update: <что>`.
- Для изменений в коде/документации, сделанных Claude Code, работай в выданной
  feature-ветке и пушь `git push -u origin <branch>`. **Не создавай PR без явной просьбы.**

---

## Obsidian-синхронизация

База знаний совместима с Obsidian: всё в `knowledge/` — обычный markdown.
Vault открывается на папке `knowledge/`. Синхронизация — плагин **obsidian-git**
(автопуш каждые N минут). Поэтому формат должен оставаться чистым markdown с frontmatter,
чтобы корректно отображаться и в Obsidian, и в GitHub.

---

## Подсказки

- Не уверен в формате записи — открой `README.md` нужного раздела.
- Не уверен в данных компании/сервера — открой `knowledge/company/avsound.md`.
- Перед ответом на вопрос о клиенте/проекте — сперва поищи в базе (`search_code`),
  не выдумывай.
