#!/usr/bin/env python3
"""
AVsound Knowledge Base MCP Server
Деплой на Hetzner — даёт Claude доступ к базе знаний из любого места
"""
import os
import base64
from datetime import datetime
import httpx
from mcp.server.fastmcp import FastMCP

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "avsoundmsk-ux")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "avsound")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

mcp = FastMCP("avsound-knowledge")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


async def gh_get(path: str) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{API}{path}", headers=HEADERS)
        r.raise_for_status()
        return r.json()


async def gh_put(path: str, data: dict) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.put(f"{API}{path}", headers=HEADERS, json=data)
        r.raise_for_status()
        return r.json()


async def gh_search(query: str) -> list:
    async with httpx.AsyncClient() as c:
        r = await c.get(
            "https://api.github.com/search/code",
            headers=HEADERS,
            params={"q": f"{query} repo:{GITHUB_OWNER}/{GITHUB_REPO}"}
        )
        r.raise_for_status()
        return r.json().get("items", [])


@mcp.tool()
async def remember(category: str, title: str, content: str) -> str:
    """
    Сохранить информацию в базу знаний AVsound.
    category: clients | projects | mailings | notes | company
    """
    safe = title.replace("/", "-").replace("\\", "-").strip()
    path = f"knowledge/{category}/{safe}.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = f"# {title}\n\n> Сохранено: {now}\n\n{content}"
    encoded = base64.b64encode(body.encode()).decode()

    sha = None
    try:
        existing = await gh_get(f"/contents/{path}")
        sha = existing.get("sha")
    except Exception:
        pass

    payload = {"message": f"remember: {title}", "content": encoded, "branch": GITHUB_BRANCH}
    if sha:
        payload["sha"] = sha

    await gh_put(f"/contents/{path}", payload)
    return f"✅ Сохранено в {path}"


@mcp.tool()
async def add_client(name: str, phone: str, email: str = "", notes: str = "", tags: str = "") -> str:
    """
    Добавить клиента в базу AVsound.
    name: имя клиента или организации
    phone: телефон
    """
    now = datetime.now().strftime("%Y-%m-%d")
    body = f"---\nname: {name}\nphone: {phone}\nemail: {email}\ntags: [{tags}]\ncreated: {now}\n---\n\n# {name}\n\n**Телефон:** {phone}\n"
    if email:
        body += f"**Email:** {email}\n"
    if notes:
        body += f"\n## Заметки\n{notes}\n"
    body += "\n## История заказов\n\n"

    safe = name.replace("/", "-").replace("\\", "-").strip()
    path = f"knowledge/clients/{safe}.md"
    encoded = base64.b64encode(body.encode()).decode()

    sha = None
    try:
        existing = await gh_get(f"/contents/{path}")
        sha = existing.get("sha")
    except Exception:
        pass

    payload = {"message": f"add client: {name}", "content": encoded, "branch": GITHUB_BRANCH}
    if sha:
        payload["sha"] = sha

    await gh_put(f"/contents/{path}", payload)
    return f"✅ Клиент {name} добавлен ({path})"


@mcp.tool()
async def search_knowledge(query: str) -> str:
    """
    Поиск по базе знаний AVsound.
    """
    items = await gh_search(query)
    if not items:
        return f"Ничего не найдено по запросу: {query}"
    results = [f"- {i['path']}" for i in items[:10]]
    return f"Найдено {len(items)}:\n" + "\n".join(results)


@mcp.tool()
async def list_knowledge(category: str) -> str:
    """
    Список записей в категории.
    category: clients | projects | mailings | notes | company
    """
    try:
        items = await gh_get(f"/contents/knowledge/{category}")
        files = [i["name"].replace(".md", "") for i in items
                 if i["type"] == "file" and i["name"].endswith(".md") and i["name"] != "README.md"]
        if not files:
            return f"В разделе '{category}' пока нет записей"
        return f"Записи в {category} ({len(files)}):\n" + "\n".join(f"- {f}" for f in files)
    except Exception as e:
        return f"Ошибка: {e}"


@mcp.tool()
async def read_knowledge(category: str, title: str) -> str:
    """
    Прочитать запись из базы знаний.
    """
    path = f"knowledge/{category}/{title}.md"
    try:
        data = await gh_get(f"/contents/{path}")
        return base64.b64decode(data["content"]).decode()
    except Exception:
        return f"Запись '{title}' не найдена в {category}"


if __name__ == "__main__":
    mcp.run(transport="sse")
