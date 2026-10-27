# RetroReader — Полный реестр атомарных задач для GitHub Issues

> **Назначение:** Данный документ содержит полный список всех атомарных задач проекта (Level 4 декомпозиция).  
> **Правило:** Каждая задача ниже представляет собой **отдельный независимый GitHub Issue** с четкими входными/выходными данными, описанием на человеческом языке и критериями приемки (Definition of Done).  
> **Текущий статус репозитория:** Репозиторий очищен от кода реализации. Присутствует только чистая структура директорий с `.gitkeep`. Все задачи берутся в работу по порядку.

---

## MILESTONE 1: Инфраструктура, сборочный тулчейн и тестовый стенд

### [M1-TASK-1.1.1.1] Проверить и установить сборочные утилиты хоста (brew, ldid, dpkg)
- **Зачем:** Для сборки iOS-приложений без Xcode и упаковки в Debian-пакеты `.deb` на Mac M4 требуются системные CLI-утилиты подписи (`ldid`) и архивации пакетов (`dpkg`).
- **Входные данные:** Mac M4, Homebrew (`/opt/homebrew/bin/brew`).
- **Выходные данные:** Установленные бинарники `ldid` и `dpkg` в `$PATH`.
- **Файлы/Команды:** `brew install ldid dpkg`
- **DoD:** Вызов `ldid -v` и `dpkg-deb --version` в терминале возвращает успешный код.
- **Labels:** `milestone:m1-toolchain`, `area:infra`, `level:atomic`

---

### [M1-TASK-1.1.1.2] Склонировать Theos в ~/theos и настроить переменные окружения
- **Зачем:** Theos — основной инструмент для кросс-компиляции под 32-битные старые устройства (armv7) на современных компьютерах Mac с процессорами Apple Silicon.
- **Входные данные:** Git, доступ в сеть к GitHub.
- **Выходные данные:** Папка `~/theos` с подмодулями и экспортированные переменные `$THEOS` и `$PATH` в `~/.zshrc`.
- **Файлы/Команды:** `git clone --recursive https://github.com/theos/theos.git ~/theos`
- **DoD:** Переменная `$THEOS` указывает на валидный каталог, утилита `nic.pl` доступна из любого места терминала.
- **Labels:** `milestone:m1-toolchain`, `area:infra`, `level:atomic`

---

### [M1-TASK-1.1.1.3] Загрузить и распаковать патченый SDK iOS 9.3 в $THEOS/sdks/
- **Зачем:** В современном Xcode нет системных заголовков для iOS 9.3 и 32-битных библиотек UIKit/Foundation. Theos использует отдельную папку с заголовочными SDK.
- **Входные данные:** Архив `iPhoneOS9.3.sdk.tar.xz` (или `iPhoneOS10.3.sdk` с архитектурой `armv7`).
- **Выходные данные:** Директория `$THEOS/sdks/iPhoneOS9.3.sdk`.
- **DoD:** Внутри каталога присутствуют заголовочные файлы `System/Library/Frameworks/UIKit.framework/Headers/UIKit.h`.
- **Labels:** `milestone:m1-toolchain`, `area:infra`, `level:atomic`

---

### [M1-TASK-1.1.2.1] Создать корневой Makefile проекта для Theos
- **Зачем:** Makefile описывает компилятору Clang целевую архитектуру `armv7`, минимальную версию системы `9.3`, список исходников и линкуемые библиотеки.
- **Входные данные:** Установленный Theos.
- **Выходные данные:** Файл `Makefile` в корне проекта.
- **Параметры:** `TARGET = iphone:clang:latest:9.3`, `ARCHS = armv7`, `RetroReader_FRAMEWORKS = UIKit Foundation CoreGraphics`, `RetroReader_LIBRARIES = sqlite3 z`.
- **DoD:** Синтаксис `Makefile` корректен, при вызове `make` Theos подхватывает параметры таргета.
- **Labels:** `milestone:m1-toolchain`, `area:config`, `level:atomic`

---

### [M1-TASK-1.1.2.2] Создать файл control с метаданными Debian-пакета
- **Зачем:** На iOS под джейлбрейком приложения упаковываются и регистрируются через пакетный менеджер dpkg на основе файла `control`.
- **Входные данные:** Идентификатор бандла и метаданные проекта.
- **Выходные данные:** Файл `control` в корне проекта со свойствами `Package: com.retroread.app`, `Name: RetroReader`, `Architecture: iphoneos-arm`, `Section: Applications`.
- **DoD:** Файл валидируется стандартной командой `dpkg-deb`.
- **Labels:** `milestone:m1-toolchain`, `area:config`, `level:atomic`

---

### [M1-TASK-1.1.2.3] Создать Info.plist приложения для iPad
- **Зачем:** iOS определяет точку входа, ориентации экрана, семейство устройств и права приложения через `Info.plist`.
- **Входные данные:** Требования к планшету iPad 2 (Landscape/Portrait, `UIDeviceFamily = [2]`).
- **Выходные данные:** Файл `resources/Info.plist`.
- **DoD:** Валидный XML plist, содержащий `CFBundleExecutable`, `CFBundleIdentifier = com.retroread.app` и `LSRequiresIPhoneOS = true`.
- **Labels:** `milestone:m1-toolchain`, `area:config`, `level:atomic`

---

### [M1-TASK-1.1.2.4] Создать Entitlements.plist для работы без песочницы
- **Зачем:** Для чтения книг из кэша и свободного взаимодействия с файловой системой на джейлбрейкнутом устройстве требуется корректный файл прав.
- **Выходные данные:** Файл `resources/Entitlements.plist`.
- **DoD:** Файл содержит флаги ad-hoc подписи для утилиты `ldid`.
- **Labels:** `milestone:m1-toolchain`, `area:config`, `level:atomic`

---

### [M1-TASK-1.1.3.1] Написать минимальный main.m и AppDelegate для Smoke-теста
- **Зачем:** Проверить сборочную цепочку на самом простом примере окна, выводящего белое окно и лог в консоль.
- **Входные данные:** Созданный `Makefile`.
- **Выходные данные:** Файлы `src/main.m`, `src/Core/AppDelegate.h`, `src/Core/AppDelegate.m`.
- **DoD:** `AppDelegate` создает `UIWindow`, задает белый фон и вызывает `makeKeyAndVisible`.
- **Labels:** `milestone:m1-toolchain`, `area:core`, `level:atomic`

---

### [M1-TASK-1.1.3.2] Настроить сборку пакета через make package на Mac M4
- **Зачем:** Проверить, что компилятор на процессоре Apple Silicon корректно линкует 32-битный бинарник под старый iOS.
- **Входные данные:** Исходники из предыдущей задачи.
- **Выходные данные:** Созданный пакет `.theos/packages/com.retroread.app_*.deb`.
- **DoD:** Команда `make package` завершается с кодом возврата 0 без ошибок линкера.
- **Labels:** `milestone:m1-toolchain`, `area:build`, `level:atomic`

---

### [M1-TASK-1.1.3.3] Проверить бинарник через утилиту file (Mach-O arm_v7)
- **Зачем:** Убедиться, что на выходе получился именно 32-битный код под A5 процессор, а не x86 или arm64.
- **Входные данные:** Скомпилированный бинарник `.theos/obj/debug/RetroReader.app/RetroReader`.
- **Выходные данные:** Вывод команды `file`.
- **DoD:** Строка в консоли содержит: `Mach-O executable arm_v7`.
- **Labels:** `milestone:m1-toolchain`, `area:qa`, `level:atomic`

---

### [M1-TASK-1.2.1.1] Загрузить IPA Phoenix4.ipa и утилиту Sideloadly на Mac M4
- **Зачем:** Phoenix — это полупривязанный джейлбрейк для iOS 9.3.5 / 9.3.6.
- **Входные данные:** Mac M4, доступ в интернет.
- **Выходные данные:** Загруженные `Phoenix4.ipa` и `Sideloadly.dmg`.
- **DoD:** Файлы скачаны и готовы к установке.
- **Labels:** `milestone:m1-toolchain`, `area:device`, `level:atomic`

---

### [M1-TASK-1.2.1.2] Подключить iPad 2 по кабелю и прошить Phoenix через Sideloadly
- **Зачем:** Установить приложение-активатор джейлбрейка на планшет с бесплатным сертификатом разработчика.
- **Входные данные:** iPad 2, подключенный по кабелю 30-pin -> USB.
- **Выходные данные:** Иконка Phoenix на домашнем экране iPad 2.
- **DoD:** В *Настройки -> Основные -> Управление устройством* профиль помечен как «Доверенный».
- **Labels:** `milestone:m1-toolchain`, `area:device`, `level:atomic`

---

### [M1-TASK-1.2.1.3] Активировать джейлбрейк на iPad 2 и дождаться установки Cydia
- **Зачем:** Получить root-доступ к операционной системе планшета.
- **Входные данные:** Установленный Phoenix на планшете.
- **Выходные данные:** Иконка магазина Cydia на рабочем столе планшета после респринга/перезагрузки.
- **DoD:** Cydia открывается и обновляет каталоги пакетов.
- **Labels:** `milestone:m1-toolchain`, `area:device`, `level:atomic`

---

### [M1-TASK-1.2.2.1] Установить OpenSSH из Cydia и задать dev-пароль
- **Зачем:** SSH позволяет управлять iPad 2 удаленно по локальной сети Wi-Fi прямо из терминала Mac M4.
- **Входные данные:** Запущенная Cydia.
- **Выходные данные:** Работающий демон `sshd` на iPad 2.
- **DoD:** Команда `ssh root@<IP_АЙПАДА>` успешно запрашивает пароль и открывает оболочку bash на планшете.
- **Labels:** `milestone:m1-toolchain`, `area:device`, `level:atomic`

---

### [M1-TASK-1.2.2.2] Установить твик AppSync Unified из cydia.akemi.ai
- **Зачем:** AppSync Unified отключает валидацию цифровой подписи Apple, позволяя ставить любые собранные приложения навсегда без недельного таймера.
- **Входные данные:** Репозиторий `https://cydia.akemi.ai/`.
- **Выходные данные:** Установленный твик AppSync Unified.
- **DoD:** Планшет разрешает установку приложений без подписи App Store.
- **Labels:** `milestone:m1-toolchain`, `area:device`, `level:atomic`

---

### [M1-TASK-1.2.2.3] Настроить беспарольный вход по SSH-ключам с Mac M4 на iPad 2
- **Зачем:** Чтобы сборка и деплой кода не прерывались запросом пароля каждый раз.
- **Входные данные:** Публичный SSH ключ Mac M4.
- **Выходные данные:** Запись ключа в `/var/root/.ssh/authorized_keys` на планшете.
- **DoD:** Команда `ssh root@<IP_АЙПАДА> "uname -a"` выполняется мгновенно без запроса пароля.
- **Labels:** `milestone:m1-toolchain`, `area:infra`, `level:atomic`

---

### [M1-TASK-1.2.2.4] Настроить THEOS_DEVICE_IP в Makefile и проверить make install
- **Зачем:** Автоматизировать цикл разработки «написал код -> нажал кнопку -> код работает на планшете».
- **Входные данные:** Локальный IP iPad 2 в сети Wi-Fi.
- **Выходные данные:** Переменная `THEOS_DEVICE_IP` в `Makefile`.
- **DoD:** Вызов `make install` собирает deb, загружает его на iPad, устанавливает и запускает приложение.
- **Labels:** `milestone:m1-toolchain`, `area:infra`, `level:atomic`

---

## MILESTONE 2: Офлайн-словарь и морфология (NLP Engine)

---

### [M2-TASK-2.1.1.1] Подготовить текстовый исходник англо-русского словаря
- **Зачем:** Нам нужен исходный словарь общего лексикона (Mueller или FreeDict) без проприетарных лицензий.
- **Входные данные:** Открытая база словаря в формате TXT или TSV.
- **Выходные данные:** Файл `tools/dict_builder/raw/source_dict.txt`.
- **DoD:** Файл содержит не менее 40 000 словарных статей на английском языке.
- **Labels:** `milestone:m2-dictionary`, `area:data`, `level:atomic`

---

### [M2-TASK-2.1.1.2] Написать парсер-нормализатор на Python для очистки данных
- **Зачем:** Исходные словари содержат HTML-разметку, битые кодировки и мусорные теги.
- **Входные данные:** `source_dict.txt`.
- **Выходные данные:** Модуль очистки в `tools/dict_builder/build_dict.py`.
- **DoD:** Функция очищает строки от тегов, пробелов, спецсимволов и приводит слова к lowercase.
- **Labels:** `milestone:m2-dictionary`, `area:script`, `level:atomic`

---

### [M2-TASK-2.1.1.3] Структурировать словарные статьи на поля (word, trans, pos, trn)
- **Зачем:** Для быстрого поиска и раздельного вывода в интерфейсе данные должны лежать в строгой структуре.
- **Входные данные:** Очищенный поток словарных данных.
- **Выходные данные:** Кортежи `(word, transcription, part_of_speech, translation)`.
- **DoD:** Поле слова не содержит пунктуации, перевод выделен в отдельную строку.
- **Labels:** `milestone:m2-dictionary`, `area:data`, `level:atomic`

---

### [M2-TASK-2.1.2.1] Написать DDL-схему таблицы words в SQLite с NOCASE индексом
- **Зачем:** Поиск по `COLLATE NOCASE` B-Tree индексу выполняется за O(log N) и не чувствителен к регистру первой буквы.
- **Выходные данные:** DDL в `tools/dict_builder/build_dict.py`:
  ```sql
  CREATE TABLE words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL COLLATE NOCASE, transcription TEXT, pos TEXT, translation TEXT NOT NULL);
  CREATE UNIQUE INDEX idx_word_nocase ON words(word COLLATE NOCASE);
  ```
- **DoD:** Схема создает таблицу и уникальный индекс без ошибок.
- **Labels:** `milestone:m2-dictionary`, `area:db`, `level:atomic`

---

### [M2-TASK-2.1.2.2] Настроить пакетную вставку транзакциями в SQLite
- **Зачем:** Вставка 50 000 строк по одной занимает несколько минут; единая транзакция выполняет это за 0.5 секунды.
- **Входные данные:** Список словарных кортежей.
- **Выходные данные:** Блок `cursor.executemany(...)` внутри транзакции.
- **DoD:** Время генерации базы на Mac M4 составляет менее 2 секунд.
- **Labels:** `milestone:m2-dictionary`, `area:script`, `level:atomic`

---

### [M2-TASK-2.1.2.3] Применить PRAGMA настройки для чтения на медленной flash-памяти iPad 2
- **Зачем:** Флеш-память iPad 2 2011 года медленная. Оптимизация `page_size = 4096` и отключение журнала ускоряют произвольное чтение.
- **Выходные данные:** Вызов `PRAGMA page_size = 4096; PRAGMA journal_mode = OFF; VACUUM; ANALYZE;`.
- **DoD:** База дефрагментирована и оптимизирована под чтение.
- **Labels:** `milestone:m2-dictionary`, `area:db`, `level:atomic`

---

### [M2-TASK-2.1.2.4] Добавить валидацию размера итогового dictionary.sqlite (до 20 МБ)
- **Зачем:** Защитить приложение от раздувания размера бандла и перерасхода памяти планшета.
- **Выходные данные:** Файл `resources/dictionary.sqlite`.
- **DoD:** Размер файла на диске не превышает 20 МБ, тестовый SELECT возвращает перевод.
- **Labels:** `milestone:m2-dictionary`, `area:qa`, `level:atomic`

---

### [M2-TASK-2.2.1.1] Добавить линковку с libsqlite3 в конфигурацию сборки
- **Зачем:** Использовать системную C-библиотеку SQLite из состава iOS SDK.
- **Выходные данные:** Флаг `-lsqlite3` в `Makefile`.
- **DoD:** Заголовок `#import <sqlite3.h>` успешно компилируется в проекте.
- **Labels:** `milestone:m2-dictionary`, `area:build`, `level:atomic`

---

### [M2-TASK-2.2.1.2] Создать модель словарной статьи RRWordEntry
- **Зачем:** Хранить найденное слово и его атрибуты в удобном Objective-C объекте.
- **Выходные данные:** Класс `src/Dictionary/RRWordEntry.h / .m` со свойствами `word`, `transcription`, `partOfSpeech`, `translation`.
- **DoD:** Объект инициализируется методом `initWithWord:transcription:partOfSpeech:translation:`.
- **Labels:** `milestone:m2-dictionary`, `area:core`, `level:atomic`

---

### [M2-TASK-2.2.1.3] Создать синглтон RRDictionaryService и метод открытия базы
- **Зачем:** Обеспечить единую точку доступа к словарю без постоянного переоткрытия файла с диска.
- **Выходные данные:** `src/Dictionary/RRDictionaryService.h / .m`, метод `openDatabaseWithPath:error:`.
- **DoD:** База открывается в режиме `SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX`.
- **Labels:** `milestone:m2-dictionary`, `area:core`, `level:atomic`

---

### [M2-TASK-2.2.1.4] Скомпилировать постоянный sqlite3_prepare_v2 стейтмент
- **Зачем:** Не тратить ресурсы CPU A5 на компиляцию SQL-запроса при каждом тапе по слову.
- **Выходные данные:** Дескриптор `sqlite3_stmt *_lookupStmt` для запроса `SELECT transcription, pos, translation FROM words WHERE word = ? LIMIT 1;`.
- **DoD:** Подготовленный запрос создается один раз при открытии базы и финализируется при закрытии.
- **Labels:** `milestone:m2-dictionary`, `area:perf`, `level:atomic`

---

### [M2-TASK-2.2.2.1] Реализовать метод очистки слова cleanWord:
- **Зачем:** При клике в тексте слово может захватывать запятые, кавычки, скобки и дефисы (например, `"word,"` -> `"word"`).
- **Выходные данные:** Метод `- (NSString *)cleanWord:(NSString *)rawWord;` в `RRDictionaryService`.
- **DoD:** Знаки `.,!?;:"'“”‘’()[]-` корректно обрезаются с краев слова.
- **Labels:** `milestone:m2-dictionary`, `area:nlp`, `level:atomic`

---

### [M2-TASK-2.2.2.2] Инициализировать NSLinguisticTagger со схемой Lemma
- **Зачем:** Использовать встроенные системные алгоритмы морфологии Apple для английского языка без тяжелых сторонних библиотек.
- **Выходные данные:** Инициализированный экземпляр `NSLinguisticTagger` со схемой `NSLinguisticTagSchemeLemma`.
- **DoD:** Объект tagger создается один раз в `init` сервиса.
- **Labels:** `milestone:m2-dictionary`, `area:nlp`, `level:atomic`

---

### [M2-TASK-2.2.2.3] Реализовать метод lemmatizeWord: для поиска инфинитивов
- **Зачем:** Приводить слова во множественном числе и временах к словарной форме (*running* -> *run*, *leaves* -> *leave*).
- **Выходные данные:** Метод `- (NSString *)lemmatizeWord:(NSString *)rawWord;`.
- **DoD:** Вызов со словом *"running"* возвращает *"run"*, со словом *"better"* возвращает *"good"*.
- **Labels:** `milestone:m2-dictionary`, `area:nlp`, `level:atomic`

---

### [M2-TASK-2.2.2.4] Реализовать двухфазный метод поиска lookupWord:
- **Зачем:** Сначала искать точную форму слова; если слово изменено — искать его лемму.
- **Выходные данные:** Метод `- (RRWordEntry *)lookupWord:(NSString *)word;`.
- **DoD:** Возвращает объект `RRWordEntry` с переводом или `nil`, если слово отсутствует.
- **Labels:** `milestone:m2-dictionary`, `area:core`, `level:atomic`

---

### [M2-TASK-2.2.2.5] Написать юнит-тест проверки словаря и лемматизации
- **Зачем:** Гарантировать стабильность работы модуля словаря до интеграции в UI.
- **Выходные данные:** Тестовый файл `tests/test_dictionary.m`.
- **DoD:** Тест проверяет 20 контрольных слов разных частей речи и завершается с `assert = OK`.
- **Labels:** `milestone:m2-dictionary`, `area:qa`, `level:atomic`

---

## MILESTONE 3: Парсинг и распаковка EPUB (EPUB Engine)

---

### [M3-TASK-3.1.1.1] Подключить системную библиотеку libz в Makefile
- **Зачем:** Использовать алгоритм DEFLATE для распаковки ZIP-контейнера EPUB.
- **Выходные данные:** Добавлен флаг `-lz` в сборочный конфиг.
- **DoD:** Заголовочный файл `#import <zlib.h>` успешно компилируется.
- **Labels:** `milestone:m3-epub`, `area:build`, `level:atomic`

---

### [M3-TASK-3.1.1.2] Разработать парсер структуры ZIP Central Directory (EOCD)
- **Зачем:** Чтение центральной директории в конце ZIP-файла дает точные смещения и размеры файлов без чтения всего архива в RAM.
- **Выходные данные:** Структуры `ZipEndOfCentralDir`, `ZipCentralDirHeader`, `ZipLocalHeader` в `src/Epub/RRZipExtractor.m`.
- **DoD:** Парсер находит маркер `0x06054b50` и считывает список файлов книги.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.1.1.3] Реализовать потоковую декомпрессию через zlib inflateInit2
- **Зачем:** Читать архив небольшими кусками по 4 КБ для защиты от вылетов по нехватке памяти (Jetsam).
- **Выходные данные:** Функция распаковки потока DEFLATE с параметром `-MAX_WBITS`.
- **DoD:** Сжатые HTML-главы распаковываются на диск байт-в-байт без повреждений.
- **Labels:** `milestone:m3-epub`, `area:perf`, `level:atomic`

---

### [M3-TASK-3.1.1.4] Создать класс-фасад RRZipExtractor
- **Зачем:** Предоставить удобный публичный интерфейс для остального приложения.
- **Выходные данные:** `src/Epub/RRZipExtractor.h / .m`, метод `+ (BOOL)unzipFileAtPath:toDestination:error:`.
- **DoD:** Метод возвращает `YES` при успешной распаковке и заполняет `NSError` при ошибке.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.1.2.1] Реализовать генерацию пути кэша книги по ее хешу
- **Зачем:** Хранить распакованные книги в стандартном каталоге кэша системы `Library/Caches/Books/<hash>/`.
- **Выходные данные:** Метод `+ (NSString *)cacheDirectoryForBookPath:(NSString *)filePath;`.
- **DoD:** Возвращает стабильный уникальный путь на основе MD5/SHA хеша исходного файла книги.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.1.2.2] Добавить проверку существующего кэша книги
- **Зачем:** Не распаковывать zip-архив заново при каждом открытии уже прочитанной книги.
- **Выходные данные:** Проверка `[NSFileManager fileExistsAtPath:containerXmlPath]`.
- **DoD:** Если книга уже распакована, повторный запуск пропускает шаг разархивации.
- **Labels:** `milestone:m3-epub`, `area:perf`, `level:atomic`

---

### [M3-TASK-3.2.1.1] Создать SAX-парсер RRContainerXMLParser для container.xml
- **Зачем:** EPUB спецификация требует найти путь к файлу описания книги через `META-INF/container.xml`. Потоковый SAX-парсер не создает дерево объектов в RAM.
- **Выходные данные:** Класс `RRContainerXMLParser` реализующий `NSXMLParserDelegate`.
- **DoD:** Корректно перехватывает тег `<rootfile>` и считывает атрибут `full-path`.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.1.2] Извлечь относительный путь к content.opf
- **Зачем:** Получить точный путь к файлу метаданных книги (например `OEBPS/content.opf`).
- **Выходные данные:** Свойство `opfRelativePath` в модели парсера.
- **DoD:** Значение свойства совпадает с реальным расположением `.opf` файла на диске.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.2.1] Создать модель главы книги RRChapterModel
- **Зачем:** Представлять отдельную главу книги с метаданными и путями к HTML.
- **Выходные данные:** `src/Epub/RRChapterModel.h / .m` со свойствами `chapterId`, `title`, `relativeHtmlPath`, `absoluteHtmlPath`, `orderIndex`.
- **DoD:** Класс компилируется и предоставляет информативный метод `description`.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.2.2] Создать модель книги RRBookModel
- **Зачем:** Хранить заголовок книги, автора, базовый путь и упорядоченный массив всех глав `NSArray<RRChapterModel *>`.
- **Выходные данные:** `src/Epub/RRBookModel.h / .m`.
- **DoD:** Модель хранит список глав и метаданные книги.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.2.3] Создать SAX-парсер RROpfXMLParser для content.opf
- **Зачем:** Распарсить метаданные книги (название, автор) и список файлов книги.
- **Выходные данные:** Класс `RROpfXMLParser` с делегатом `NSXMLParserDelegate`.
- **DoD:** Корректно извлекает текст из `<dc:title>` и `<dc:creator>`.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.2.4] Распарсить секцию manifest (сопоставление id -> href)
- **Зачем:** Сопоставить уникальные строковые ID глав с их физическими именами HTML-файлов.
- **Выходные данные:** Словарь `NSMutableDictionary<NSString *, NSString *> *manifest` в `RROpfXMLParser`.
- **DoD:** Содержит пары вида `chapter1 -> chapter1.xhtml`.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.2.5] Распарсить секцию spine (линейный порядок чтения)
- **Зачем:** Книга должна читаться в строгом авторском порядке, заданном списком `<itemref idref="...">`.
- **Выходные данные:** Массив `NSMutableArray<NSString *> *spine` в `RROpfXMLParser`.
- **DoD:** Порядок элементов массива точно соответствует порядку глав в книге.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

### [M3-TASK-3.2.2.6] Реализовать фасад RREpubParser с методом parseEpubAtPath:
- **Зачем:** Объединить распаковку и оба этапа XML-парсинга в один простой метод.
- **Выходные данные:** `src/Epub/RREpubParser.h / .m`, метод `+ (RRBookModel *)parseEpubAtPath:(NSString *)path error:(NSError **)error;`.
- **DoD:** Возвращает полностью собранную `RRBookModel` с существующими файлами глав.
- **Labels:** `milestone:m3-epub`, `area:core`, `level:atomic`

---

## MILESTONE 4: Читалка и перехват кликов (UIWebView + JS Bridge)

---

### [M4-TASK-4.1.1.1] Создать RRReaderViewController и настроить UIWebView
- **Зачем:** Основной экран чтения на iPad 2.
- **Выходные данные:** `src/Reader/RRReaderViewController.h / .m`.
- **DoD:** В `viewDidLoad` создается `UIWebView`, растянутый на весь экран `self.view.bounds`.
- **Labels:** `milestone:m4-reader`, `area:ui`, `level:atomic`

---

### [M4-TASK-4.1.1.2] Отключить лишний скролл и системный оверхед WebView
- **Зачем:** Сэкономить оперативную память и отключить стандартное поведение браузера (пружинящий скролл).
- **Выходные данные:** `self.webView.scrollView.bounces = NO; self.webView.scrollView.scrollEnabled = NO;`.
- **DoD:** WebView не скроллится вертикально пальцем.
- **Labels:** `milestone:m4-reader`, `area:perf`, `level:atomic`

---

### [M4-TASK-4.1.1.3] Отключить системные детекторы типов данных
- **Зачем:** Чтобы iOS 9 не тратила CPU на поиск телефонных номеров, адресов и ссылок в тексте книги.
- **Выходные данные:** `self.webView.dataDetectorTypes = UIDataDetectorTypeNone;`.
- **DoD:** Текст отображается как чистый контент без системных подчеркиваний ссылок.
- **Labels:** `milestone:m4-reader`, `area:perf`, `level:atomic`

---

### [M4-TASK-4.1.2.1] Создать reader_style.css с версткой CSS Multi-Column
- **Зачем:** Разбить длинный HTML-текст главы на горизонтальные страницы размером с экран iPad без тяжелых JS библиотек.
- **Выходные данные:** Файл `src/Reader/Assets/reader_style.css` со свойствами `-webkit-column-width: 924px; -webkit-column-gap: 100px;`.
- **DoD:** Текст форматируется в страницы, пролистываемые по горизонтали.
- **Labels:** `milestone:m4-reader`, `area:css`, `level:atomic`

---

### [M4-TASK-4.1.2.2] Отключить системное синее выделение текста в CSS
- **Зачем:** Стандартная лупа и выделение iOS мешают плавному тапу по словам для перевода.
- **Выходные данные:** Свойства `-webkit-touch-callout: none; -webkit-user-select: none;` в CSS.
- **DoD:** Долгий тап по тексту не вызывает системное меню копирования/выделения.
- **Labels:** `milestone:m4-reader`, `area:css`, `level:atomic`

---

### [M4-TASK-4.1.2.3] Реализовать инъекцию reader_style.css в тег <head> главы
- **Зачем:** Применять единые стили чтения ко всем главам любой книги.
- **Выходные данные:** Метод подготовки HTML в `RRReaderViewController`.
- **DoD:** Стили вставляются внутрь `<head>` перед передачей в `loadHTMLString:baseURL:`.
- **Labels:** `milestone:m4-reader`, `area:core`, `level:atomic`

---

### [M4-TASK-4.1.2.4] Обернуть содержимое <body> в <div id="book-container">
- **Зачем:** Изолировать геометрию колонок внутри контролируемого контейнера с отступами.
- **Выходные данные:** Модификация HTML в методе загрузки главы.
- **DoD:** Контент главы находится внутри `#book-container`.
- **Labels:** `milestone:m4-reader`, `area:core`, `level:atomic`

---

### [M4-TASK-4.1.2.5] Реализовать сдвиг пагинации через window.scrollTo
- **Зачем:** Мгновенный и плавный переход между страницами внутри главы.
- **Выходные данные:** JS-метод `window.RRScrollToPage(pageIndex)` и вызов `stringByEvaluatingJavaScriptFromString:`.
- **DoD:** Вызов функции сдвигает страницу ровно на `pageIndex * 1024px`.
- **Labels:** `milestone:m4-reader`, `area:core`, `level:atomic`

---

### [M4-TASK-4.1.2.6] Добавить свайпы влево и вправо для перелистывания страниц
- **Зачем:** Нативное управление чтением свайпом пальца.
- **Выходные данные:** Экземпляры `UISwipeGestureRecognizer` для направлений Left и Right на `self.webView`.
- **DoD:** Свайп влево листает вперед, свайп вправо листает назад.
- **Labels:** `milestone:m4-reader`, `area:ui`, `level:atomic`

---

### [M4-TASK-4.1.2.7] Создать панели с названием книги и номерами страниц
- **Зачем:** Показывать читателю прогресс чтения и текущую главу.
- **Выходные данные:** `headerBar` с названием книги и `footerBar` с лейблом «Глава X • Стр. Y из Z».
- **DoD:** Номера страниц динамически обновляются при перелистывании.
- **Labels:** `milestone:m4-reader`, `area:ui`, `level:atomic`

---

### [M4-TASK-4.2.1.1] Создать reader_bridge.js со слушателем клика по документу
- **Зачем:** Перехватывать пользовательские нажатия на экран для определения нажатого слова.
- **Выходные данные:** Файл `src/Reader/Assets/reader_bridge.js`, слушатель `document.addEventListener('click', ...)`.
- **DoD:** Клик по тексту перехватывается скриптом.
- **Labels:** `milestone:m4-reader`, `area:js`, `level:atomic`

---

### [M4-TASK-4.2.1.2] Реализовать поиск позиции текста через caretRangeFromPoint
- **Зачем:** Встроенный браузерный API WebKit возвращает точный текстовый узел под координатами тапа `(e.clientX, e.clientY)`.
- **Выходные данные:** Вызов `document.caretRangeFromPoint(e.clientX, e.clientY)`.
- **DoD:** Скрипт получает валидный объект `Range` в месте касания.
- **Labels:** `milestone:m4-reader`, `area:js`, `level:atomic`

---

### [M4-TASK-4.2.1.3] Расширить диапазон до границы слова и очистить пунктуацию
- **Зачем:** Получить слово целиком, даже если пользователь нажал на крайнюю букву.
- **Выходные данные:** Вызов `range.expand('word')` и регулярное выражение очистки пунктуации.
- **DoD:** Выделяется только чистое слово без точек и запятых.
- **Labels:** `milestone:m4-reader`, `area:js`, `level:atomic`

---

### [M4-TASK-4.2.1.4] Вычислить экранный прямоугольник слова через getBoundingClientRect
- **Зачем:** Узнать точные координаты `(x, y, width, height)` слова для привязки стрелочки всплывающего бабла.
- **Выходные данные:** Объект `var rect = range.getBoundingClientRect();`.
- **DoD:** Координаты соответствуют положению слова на экране iPad.
- **Labels:** `milestone:m4-reader`, `area:js`, `level:atomic`

---

### [M4-TASK-4.2.1.5] Сформировать URL кастомной схемы reader-bridge://
- **Зачем:** Передать слово и его координаты из веб-контейнера в нативный код Objective-C.
- **Выходные данные:** Строка `window.location.href = 'reader-bridge://wordTap?word=...&x=...&y=...&w=...&h=...';`.
- **DoD:** Браузер инициирует переход по кастомному URL.
- **Labels:** `milestone:m4-reader`, `area:js`, `level:atomic`

---

### [M4-TASK-4.2.2.1] Реализовать перехват схемы reader-bridge в UIWebViewDelegate
- **Зачем:** Перехватить запрос из JS до того, как веб-представление попытается загрузить несуществующую веб-страницу.
- **Выходные данные:** Метод `webView:shouldStartLoadWithRequest:navigationType:` в `RRReaderViewController`.
- **DoD:** При схеме `reader-bridge` метод возвращает `NO` и вызывает нативный обработчик.
- **Labels:** `milestone:m4-reader`, `area:core`, `level:atomic`

---

### [M4-TASK-4.2.2.2] Распарсить query-параметры перехваченного URL
- **Зачем:** Извлечь строку слова и числовые координаты `x`, `y`, `w`, `h`.
- **Выходные данные:** Использование `NSURLComponents` и массива `queryItems`.
- **DoD:** Формируется структура `CGRect` слова на экране.
- **Labels:** `milestone:m4-reader`, `area:core`, `level:atomic`

---

## MILESTONE 5: Всплывающий бабл с переводом (Popover UI)

---

### [M5-TASK-5.1.1.1] Создать класс контроллера RRTranslationViewController
- **Зачем:** Отображение словарной карточки внутри всплывающего окна iPad.
- **Выходные данные:** `src/Popover/RRTranslationViewController.h / .m`.
- **DoD:** Контроллер задает `self.preferredContentSize = CGSizeMake(300, 160)`.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.1.2] Сверстать UILabel для слова и транскрипции
- **Зачем:** Четкое визуальное отображение оригинального слова и произношения.
- **Выходные данные:** `lblWord` (19pt bold) и `lblTranscription` (13pt italic).
- **DoD:** Элементы аккуратно размещены в верхней части попапа.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.1.3] Добавить цветной бейдж части речи
- **Зачем:** Наглядно показывать грамматическую категорию слова (noun, verb, adj).
- **Выходные данные:** `lblPos` со скруглением углов 4px и фоновым цветом.
- **DoD:** Бейдж отображается справа от слова, если часть речи указана в словаре.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.1.4] Добавить UITextView для текста перевода со скроллом
- **Зачем:** Словарные статьи могут быть длинными; текст должен удобно прокручиваться.
- **Выходные данные:** `txtTranslation` с параметрами `editable = NO; selectable = NO;`.
- **DoD:** Текст перевода читаем и прокручивается при превышении высоты поля.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.2.1] Настроить modalPresentationStyle = UIModalPresentationPopover
- **Зачем:** Использовать нативный механизм баблов iPadOS.
- **Выходные данные:** Конфигурация контроллера перед презентацией.
- **DoD:** Окно открывается как парящий бабл, а не модальный диалог на весь экран.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.2.2] Привязать sourceView и sourceRect к координатам слова
- **Зачем:** Чтобы стрелочка бабла указывала прямо на нажатое в книге слово.
- **Выходные данные:** `popPresenter.sourceView = self.webView; popPresenter.sourceRect = wordRect;`.
- **DoD:** Стрелочка точно позиционируется относительно слова.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.2.3] Настроить разрешенные направления стрелочки
- **Зачем:** Бабл должен гармонично раскрываться вверх или вниз в зависимости от положения слова на экране.
- **Выходные данные:** `permittedArrowDirections = UIPopoverArrowDirectionUp | UIPopoverArrowDirectionDown;`.
- **DoD:** Стрелочка не выходит за границы экрана.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

### [M5-TASK-5.1.2.4] Реализовать adaptivePresentationStyle с UIModalPresentationNone
- **Зачем:** Запретить iOS адаптивно разворачивать попап на весь экран планшета.
- **Выходные данные:** Делегат `adaptivePresentationStyleForPresentationController:` возвращает `UIModalPresentationNone`.
- **DoD:** На iPad всегда отображается компактный бабл.
- **Labels:** `milestone:m5-popover`, `area:ui`, `level:atomic`

---

## MILESTONE 6: Оптимизация памяти (512 MB RAM) и релизная сборка

---

### [M6-TASK-6.1.1.1] Реализовать сброс кэша в didReceiveMemoryWarning
- **Зачем:** При приближении к лимиту памяти iPad 2 (Jetsam kill) очистить системный дисковый и оперативный кэш.
- **Выходные данные:** `[[NSURLCache sharedURLCache] removeAllCachedResponses];` в `didReceiveMemoryWarning`.
- **DoD:** При получении системного предупреждения кэш очищается, приложение не крашится.
- **Labels:** `milestone:m6-release`, `area:perf`, `level:atomic`

---

### [M6-TASK-6.1.1.2] Выгружать неактивные главы книги из DOM памяти
- **Зачем:** Не накапливать прочитанные главы в памяти WebView.
- **Выходные данные:** Загрузка только одной текущей главы в `loadHTMLString:`.
- **DoD:** Память процесса не растет при переходе между десятками глав.
- **Labels:** `milestone:m6-release`, `area:perf`, `level:atomic`

---

### [M6-TASK-6.1.1.3] Добавить сброс кэша в applicationDidEnterBackground
- **Зачем:** Защитить приложение от выгрузки системой, когда пользователь временно сворачивает планшет.
- **Выходные данные:** Обработчик в `AppDelegate.m`.
- **DoD:** При сворачивании память приложения падает до минимума.
- **Labels:** `milestone:m6-release`, `area:perf`, `level:atomic`

---

### [M6-TASK-6.1.2.1] Подготовить демо-книгу sample.epub (Алиса в Стране чудес)
- **Зачем:** Чтобы сразу после сборки в приложении была доступна книга для проверки.
- **Выходные данные:** Валидный файл `resources/sample.epub`.
- **DoD:** Файл проходит EPUB валидацию и содержит оглавление.
- **Labels:** `milestone:m6-release`, `area:data`, `level:atomic`

---

### [M6-TASK-6.1.2.2] Настроить включение ресурсов в бандл приложения
- **Зачем:** Скомпилированный словарь и книга должны попадать внутрь установленного `.app` бандла.
- **Выходные данные:** Директива `RetroReader_RESOURCE_DIRS = resources` в `Makefile`.
- **DoD:** Внутри собранного пакета лежат `dictionary.sqlite` и `sample.epub`.
- **Labels:** `milestone:m6-release`, `area:build`, `level:atomic`

---

### [M6-TASK-6.1.2.3] Провести Smoke-тест расхода памяти на реальном iPad 2
- **Зачем:** Финальная валидация отсутствия утечек памяти на старом устройстве.
- **Выходные данные:** Замер Resident Memory через Xcode Instruments или top/ps на планшете.
- **DoD:** Потребление оперативной памяти процесса находится в пределах 35–55 МБ.
- **Labels:** `milestone:m6-release`, `area:qa`, `level:atomic`

---

## MILESTONE 7: Кастомные EPUB, Библиотека и Кастомизация ридера

### [M7-TASK-7.1.1.1] Регистрация Document Types и UTI для EPUB в Info.plist
- **Зачем:** Включение системной поддержки открытия .epub файлов из Safari, AirDrop, мессенджеров («Открыть в...») и через iTunes File Sharing по кабелю.
- **Входные данные:** `resources/Info.plist`.
- **Выходные данные:** Ключи `CFBundleDocumentTypes`, `UTImportedTypeDeclarations`, `UIFileSharingEnabled = YES`, `LSSupportsOpeningDocumentsInPlace = NO`.
- **DoD:** Система распознает файлы с расширением .epub как принадлежащие RetroReader; папка документов видна в iTunes.
- **Labels:** `milestone:m7-features`, `area:config`, `level:atomic`

---

### [M7-TASK-7.1.1.2] Обработка входящих EPUB-файлов и URL в AppDelegate
- **Зачем:** Перехват входящих файлов, отправленных через AirDrop, почту или Safari, и перемещение их в постоянное хранилище.
- **Входные данные:** Метод `application:openURL:options:` в `AppDelegate.m`.
- **Выходные данные:** Импорт файла из каталога Inbox в постоянное хранилище `Documents/Books`.
- **DoD:** При открытии внешнего .epub файла приложение сохраняет его и обновляет библиотеку.
- **Labels:** `milestone:m7-features`, `area:core`, `level:atomic`

---

### [M7-TASK-7.1.1.3] Менеджер хранилища книг RRBookStorageManager
- **Зачем:** Изолированное управление каталогами книг, кэшами распакованных глав и метаданными.
- **Входные данные:** `Documents/Books` и встроенный `sample.epub`.
- **Выходные данные:** Класс `RRBookStorageManager` с методами `loadAllBooks`, `importEpubFromURL:`, `deleteBook:`.
- **DoD:** Корректный поиск всех доступных .epub в документах и бандле, автосоздание папки книг и очистка кэша.
- **Labels:** `milestone:m7-features`, `area:storage`, `level:atomic`

---

### [M7-TASK-7.2.1.1] Экран книжной полки RRBookShelfViewController
- **Зачем:** Удобный графический интерфейс со списком доступных книг (обложка, название, автор, количество глав).
- **Входные данные:** Список моделей `RRBookModel` от `RRBookStorageManager`.
- **Выходные данные:** Класс `RRBookShelfViewController` с табличным/сеточным представлением и поддержкой удаления книг.
- **DoD:** Отображение всех доступных книг, возможность выбора книги для чтения и удаления ненужных книг.
- **Labels:** `milestone:m7-features`, `area:ui`, `level:atomic`

---

### [M7-TASK-7.2.1.2] Интеграция навигации Библиотека <-> Читалка
- **Зачем:** Переход из полки в читалку и обратно по кнопке в верхней панели ридера.
- **Входные данные:** `UINavigationController`, кнопка «← Полка» в `RRReaderViewController`.
- **Выходные данные:** Навигационный стек в `AppDelegate.m`, плавный переход и выгрузка памяти предыдущей книги.
- **DoD:** Тап по книге на полке открывает ридер; тап «← Полка» в ридере возвращает на книжную полку.
- **Labels:** `milestone:m7-features`, `area:ui`, `level:atomic`

---

### [M7-TASK-7.3.1.1] Модель настроек читателя RRReaderSettings
- **Зачем:** Хранение пользовательских настроек (размер шрифта, гарнитура, цветовая тема) в `NSUserDefaults`.
- **Входные данные:** `NSUserDefaults`.
- **Выходные данные:** Класс `RRReaderSettings` с сохранением параметров `fontSize`, `fontFamily`, `theme`.
- **DoD:** Настройки сохраняются между запусками приложения и применяются по умолчанию.
- **Labels:** `milestone:m7-features`, `area:core`, `level:atomic`

---

### [M7-TASK-7.3.1.2] Всплывающее меню настроек RRSettingsViewController
- **Зачем:** Удобный всплывающий поповер с кнопками регулировки размера шрифта (A-/A+), выбора гарнитуры и цветовой темы.
- **Входные данные:** Кнопка «Aa» в панели ридера.
- **Выходные данные:** Класс `RRSettingsViewController` в режиме `UIModalPresentationPopover`.
- **DoD:** Пользователь может интерактивно менять размер шрифта, тему (Светлая, Сепия, Ночь) и гарнитуру.
- **Labels:** `milestone:m7-features`, `area:ui`, `level:atomic`

---

### [M7-TASK-7.3.1.3] Динамическое обновление стилей в DOM через JS Bridge
- **Зачем:** Мгновенное применение нового размера шрифта, темы или гарнитуры без перезагрузки всей страницы.
- **Входные данные:** Функции `window.RRApplySettings`, `window.RRSetFontSize`, `window.RRSetTheme` в `reader_bridge.js`.
- **Выходные данные:** Обновление стилей `#book-container` и пересчет пагинации `RRGetTotalPages`.
- **DoD:** При изменении шрифта или темы текст мгновенно перерисовывается без мерцания и белого экрана.
- **Labels:** `milestone:m7-features`, `area:web`, `level:atomic`
