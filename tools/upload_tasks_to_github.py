#!/usr/bin/env python3
"""
Скрипт автоматического создания GitHub Issues из docs/ATOMIC_TASKS.md
Каждый атомарный подпункт создает отдельный Issue в репозитории с соответствующими тегами и описанием.
"""

import os
import sys
import re
import json
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
ATOMIC_TASKS_FILE = os.path.join(PROJECT_ROOT, "docs", "ATOMIC_TASKS.md")

def parse_atomic_tasks(file_path):
    if not os.path.exists(file_path):
        print(f"[-] Файл не найден: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Поиск блоков вида: ### [M*-TASK-*] Название задачи
    pattern = r"### \[(M\d+-TASK-[^\]]+)\] (.*?)\n(.*?)(?=(?:\n### \[M\d+-TASK-|\Z))"
    matches = re.findall(pattern, content, re.DOTALL)

    tasks = []
    for task_id, title, raw_body in matches:
        body = raw_body.strip()
        
        # Извлекаем лейблы из строки - **Labels:** `...`, `...`
        labels = []
        labels_match = re.search(r"-\s+\*\*Labels:\*\*\s*(.*)", body)
        if labels_match:
            raw_labels = labels_match.group(1)
            # Находим слова в обратных кавычках или через запятую
            extracted = re.findall(r"`([^`]+)`", raw_labels)
            if not extracted:
                extracted = [lbl.strip() for lbl in raw_labels.split(",") if lbl.strip()]
            labels = extracted

        tasks.append({
            "id": task_id,
            "title": f"[{task_id}] {title.strip()}",
            "body": body,
            "labels": labels
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
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]

    print(f"[*] Чтение атомарных задач из {ATOMIC_TASKS_FILE}...")
    tasks = parse_atomic_tasks(ATOMIC_TASKS_FILE)
    print(f"[+] Распознано атомарных задач: {len(tasks)}\n")

    for i, t in enumerate(tasks, start=1):
        labels_str = ", ".join(t["labels"]) if t["labels"] else "без лейблов"
        print(f"{i:2d}. {t['title']} (Лейблы: {labels_str})")

    if dry_run:
        print("\n[DRY RUN] Проверка парсера завершена. Все подпункты готовы к отправке в GitHub Issues.")
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
            print("Создайте токен: GitHub -> Settings -> Developer Settings -> Personal access tokens (classic) с правами 'repo'.")
            sys.exit(1)

    print(f"\n[*] Начинаем отправку всех {len(tasks)} атомарных задач в GitHub Issues репозитория {repo}...")
    created_count = 0
    for t in tasks:
        issue_url = create_issue(repo, token, t['title'], t['body'], t['labels'])
        if issue_url:
            print(f"    [OK] Создано: {issue_url}")
            created_count += 1
        else:
            print(f"    [FAIL] Не удалось создать {t['id']}")

    print(f"\n[OK] Завершено! Успешно создано {created_count} из {len(tasks)} задач в GitHub Issues.")

if __name__ == "__main__":
    main()
