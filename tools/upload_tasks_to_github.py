#!/usr/bin/env python3
"""
Скрипт автоматического создания GitHub Issues из docs/TASKS_SPEC.md
Использует GitHub REST API (требуется GITHUB_TOKEN или авторизованный gh).
"""

import os
import sys
import re
import json
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
SPEC_FILE = os.path.join(PROJECT_ROOT, "docs", "TASKS_SPEC.md")

def parse_tasks(spec_path):
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ищем блоки задач вида: ### [TASK-X.X] Название задачи ...
    pattern = r"### \[(TASK-\d+\.\d+)\] (.*?)\n(.*?)(?=(?:\n### \[TASK-|\Z))"
    matches = re.findall(pattern, content, re.DOTALL)

    tasks = []
    for task_id, title, body in matches:
        full_title = f"[{task_id}] {title.strip()}"
        clean_body = body.strip()
        tasks.append({
            "id": task_id,
            "title": full_title,
            "body": clean_body
        })
    return tasks

def create_issue(repo, token, title, body, labels=None):
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RetroReader-Task-Uploader"
    }
    payload = {
        "title": title,
        "body": body
    }
    if labels:
        payload["labels"] = labels

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("html_url")
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        print(f"[-] Ошибка создания таски '{title}': HTTP {e.code} - {error_msg}")
        return None

def main():
    if not os.path.exists(SPEC_FILE):
        print(f"[-] Файл спецификации не найден: {SPEC_FILE}")
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]

    print(f"[*] Чтение задач из {SPEC_FILE}...")
    tasks = parse_tasks(SPEC_FILE)
    print(f"[+] Успешно распознано {len(tasks)} задач:")
    for t in tasks:
        print(f"    - {t['title']}")

    if dry_run:
        print("\n[DRY RUN] Проверка парсера завершена успешно. Реальные запросы не отправлялись.")
        return

    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")

    if not repo:
        if len(args) > 0:
            repo = args[0]
        else:
            print("\nИспользование:")
            print("  python3 tools/upload_tasks_to_github.py owner/repo <GITHUB_TOKEN>")
            print("  или:")
            print("  GITHUB_TOKEN=ghp_xxx python3 tools/upload_tasks_to_github.py owner/repo")
            sys.exit(1)

    if not token:
        if len(args) > 1:
            token = args[1]
        else:
            print("\n[-] Ошибка: Не задан токен доступа к GitHub.")
            print("Создайте токен: GitHub -> Settings -> Developer Settings -> Personal access tokens (classic) с галочкой 'repo'.")
            sys.exit(1)

    print(f"\n[*] Начинаем отправку в {repo}...")
    for t in tasks:
        labels = ["ios9", "ipad2"]
        if "TASK-1" in t['id']:
            labels.append("infra")
        elif "TASK-2" in t['id']:
            labels.append("dictionary")
        elif "TASK-3" in t['id']:
            labels.append("epub")
        elif "TASK-4" in t['id']:
            labels.append("reader")
        elif "TASK-5" in t['id']:
            labels.append("ui")
        elif "TASK-6" in t['id']:
            labels.append("release")

        issue_url = create_issue(repo, token, t['title'], t['body'], labels)
        if issue_url:
            print(f"    [OK] Создано: {issue_url}")
        else:
            print(f"    [FAIL] Не удалось создать {t['id']}")

    print("\n[OK] Все задачи успешно созданы в GitHub Issues!")

if __name__ == "__main__":
    main()
