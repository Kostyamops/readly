# RetroReader (iPad 2 / iOS 9.3.5)

Offline EPUB reader with instant word-tap translation bubble for iPad 2 (Apple A5, 32-bit ARMv7, 512MB RAM, iOS 9.3.5).

---

## Статус репозитория
> **Репозиторий подготовлен к командной разработке с нуля.**  
> В репозитории создана эталонная файловая структура папок без кода и заглушек.  
> Все этапы разработки декомпозированы на **78 атомарных задач**, каждая из которых готова к переносу в GitHub Issues.

---

## Архитектура папок проекта

```text
readly/
├── docs/
│   ├── ATOMIC_TASKS.md          # 78 детальных атомарных задач для GitHub Issues
│   └── TASKS_SPEC.md            # Сводная спецификация архитектуры
├── src/
│   ├── Core/                    # AppDelegate, main.m, Constants
│   ├── Dictionary/              # RRDictionaryService, RRWordEntry
│   ├── Epub/                    # RRZipExtractor, RREpubParser, модели книг
│   ├── Reader/                  # RRReaderViewController
│   │   └── Assets/              # reader_style.css, reader_bridge.js
│   └── Popover/                 # RRTranslationViewController
├── resources/                   # dictionary.sqlite, sample.epub, Info.plist
├── tests/                       # Unit-тесты
└── tools/
    ├── upload_tasks_to_github.py # Скрипт автоматического создания всех 78 задач в GitHub Issues
    └── dict_builder/            # Скрипты подготовки словарной базы
```

---

## Реестр задач и ТЗ
- 👉 **[78 Атомарных задач для GitHub Issues (ATOMIC_TASKS.md)](file:///Users/admin/Documents/antigravity/wonderful-raman/docs/ATOMIC_TASKS.md)**
- 👉 **[Сводная спецификация проекта (TASKS_SPEC.md)](file:///Users/admin/Documents/antigravity/wonderful-raman/docs/TASKS_SPEC.md)**

---

## Автоматическая загрузка задач в GitHub Issues

В репозитории подготовлен скрипт `tools/upload_tasks_to_github.py`.  
Для загрузки всех 78 задач с тегами выполните:

```bash
# Предварительная проверка (сухой прогон):
python3 tools/upload_tasks_to_github.py --dry-run

# Реальная отправка в GitHub Issues:
GITHUB_TOKEN=ghp_ваш_токен python3 tools/upload_tasks_to_github.py <ЛОГИН>/<ИМЯ_РЕПОЗИТОРИЯ>
```
