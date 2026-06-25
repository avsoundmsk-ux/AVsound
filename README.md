# AVsound — База знаний и MCP-сервер

База знаний и инструменты компании **AVsound** (Москва, звуковое оборудование и
обслуживание мероприятий). Репозиторий совмещает две роли:

1. **База знаний** (`knowledge/`) — markdown-файлы о клиентах, проектах, рассылках,
   заметках и самой компании. Совместимы с Obsidian. Это источник правды для всей
   информации AVsound.
2. **MCP-сервер** (`mcp-server/`) — Python-сервис на FastMCP, задеплоенный на Hetzner.
   Даёт любому Claude инструменты для чтения и записи базы знаний через GitHub API.

Главный принцип: **вся постоянная информация живёт в Git**, а не только в памяти сессии.

---

## Структура

```
AVsound/
├── CLAUDE.md          # инструкция для Claude (читать первой)
├── README.md          # этот файл
├── knowledge/         # база знаний (markdown, Obsidian-совместимо)
│   ├── clients/       # клиенты: 1 файл = 1 клиент
│   ├── projects/      # проекты и мероприятия
│   ├── mailings/      # рассылки
│   ├── notes/         # свободные заметки
│   └── company/       # инфо о компании, контакты, сервер
└── mcp-server/        # MCP-сервер (Python / FastMCP)
```

В каждом разделе `knowledge/` есть `README.md` с эталонным форматом записи
(YAML frontmatter + заголовки) — сверяйся с ним перед созданием файла.

| Раздел | Путь | Что хранить |
|--------|------|-------------|
| Клиенты | `knowledge/clients/` | Контакты, телефоны, история заказов |
| Проекты | `knowledge/projects/` | Мероприятия, оборудование, задачи, дедлайны |
| Рассылки | `knowledge/mailings/` | Списки получателей, тексты, результаты |
| Заметки | `knowledge/notes/` | Идеи, инструкции, разное |
| Компания | `knowledge/company/` | Прайс, услуги, инфо об AVsound, сервер |

---

## Как пользоваться

### Через Claude
Обращайся к Claude обычными командами, например:
- «запомни клиента Иван Иванов +7 999 000 00 00»
- «запомни проект: Свадьба на 2026-07-01 для Иван Иванов»
- «найди Иван»
- «покажи клиентов»

Полный список команд и правил — в [`CLAUDE.md`](CLAUDE.md).

### Через Obsidian
Открой папку `knowledge/` как vault. Синхронизация — плагин **obsidian-git**
(автопуш каждые N минут). Формат должен оставаться чистым markdown с frontmatter,
чтобы корректно отображаться и в Obsidian, и в GitHub.

---

## MCP-сервер

Сервис на **Python 3 + FastMCP** (транспорт SSE) отдаёт 5 инструментов:
`remember`, `add_client`, `search_knowledge`, `list_knowledge`, `read_knowledge`.

Локальный запуск:
```bash
cd mcp-server
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # затем впиши GITHUB_TOKEN
python server.py            # SSE-сервер на порту 8080
```

Деплой на Hetzner и подключение к Claude Code описаны в
[`mcp-server/README.md`](mcp-server/README.md).

---

## Контакты

- **Email:** avsoundmsk@gmail.com
- **Город:** Москва
- **GitHub:** https://github.com/avsoundmsk-ux/avsound
