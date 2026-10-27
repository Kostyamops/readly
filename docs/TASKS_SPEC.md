# RetroReader — Документация и Техническое задание для разработчиков

> **Проект:** Читалка EPUB книг с мгновенным офлайн-переводом по тапу на слово для iPad 2 (iOS 9.3.5).  
> **Стек:** Objective-C, SQLite, UIWebView (CSS Multi-Column Paging), JavaScript Bridge, NSLinguisticTagger, Theos (armv7).  
> **Целевое железо:** iPad 2 (2011), процессор Apple A5 (32-bit), 512 МБ RAM.

---

## Архитектура проекта и структура папок

```text
wonderful-raman/
├── docs/
│   ├── ARCHITECTURE.md          # Общая архитектура и ограничения памяти
│   └── TASKS_SPEC.md            # Данный подробный документ с рабочими тасками (Jira-style)
├── tools/
│   └── dict_builder/
│       ├── build_dict.py        # Python-скрипт парсинга словаря в SQLite
│       ├── raw/                 # Папка с исходными текстовыми словарями
│       └── output/              # Папка куда сохраняется скомпилированный dictionary.sqlite
├── src/
│   ├── Core/
│   │   ├── AppDelegate.h / .m   # Точка входа в приложение
│   │   ├── main.m
│   │   └── Constants.h          # Глобальные константы и настройки
│   ├── Dictionary/
│   │   ├── RRDictionaryService.h / .m # Синглтон для поиска и лемматизации
│   │   └── RRWordEntry.h / .m         # Модель словарной статьи
│   ├── Epub/
│   │   ├── Minizip/             # Легковесный C-код для распаковки ZIP
│   │   │   ├── unzip.h / unzip.c
│   │   │   └── ioapi.h / ioapi.c
│   │   ├── RRZipExtractor.h / .m      # Обертка над minizip
│   │   ├── RREpubParser.h / .m        # SAX XML парсер для container.xml и content.opf
│   │   ├── RRBookModel.h / .m         # Модель книги (метаданные, список глав)
│   │   └── RRChapterModel.h / .m      # Модель отдельной главы
│   ├── Reader/
│   │   ├── RRReaderViewController.h / .m # Экран чтения (UIWebView)
│   │   ├── Assets/
│   │   │   ├── reader_bridge.js       # JS-скрипт детекции слова и координат
│   │   │   └── reader_style.css       # Стили верстки страницы в колонки
│   │   └── RRPageManager.h / .m       # Управление пагинацией и расчетом страниц
│   └── Popover/
│       └── RRTranslationViewController.h / .m # Всплывающий бабл с переводом
├── resources/
│   ├── Info.plist               # Конфиг приложения
│   ├── sample.epub              # Демо-книга для первых тестов
│   └── dictionary.sqlite        # Скомпилированная база данных словаря
├── Makefile                     # Главный файл сборки Theos
└── control                      # Метаданные Debian-пакета для iOS
```

---

## Правила кодинга для этого проекта
1. **Никакого Swift.** В iOS 9 нет стабильного ABI. Swift раздует бинарник и сожрет 30-40 МБ драгоценной RAM просто при старте. Только Objective-C (ARC включен).
2. **Память — священна.** На iPad 2 доступно всего 512 МБ RAM. Если процесс приложения превышает ~120 МБ, система принудительно убивает его по сигналу Jetsam (OOM). Поэтому:
   - Не держим весь EPUB в памяти: читаем файлы потоково.
   - Базу SQLite открываем в режиме `SQLITE_OPEN_READONLY` с кэшем не более 2 МБ.
   - Избегаем тяжелых DOM-библиотек.
3. **Все методы документируются человеческим языком.** Если пишешь хитрый трюк — оставляй комментарий, почему сделано именно так.

---

# Техническое задание по задачам (Work Breakdown Structure)

---

## MILESTONE 1: Инфраструктура, сборочный тулчейн и тестовый стенд

---

### [TASK-1.1] Настройка сборочного тулчейна Theos под 32-bit (armv7) на Mac M4

* **Простыми словами:**  
  Современный Xcode на Mac с процессором M4 не умеет собирать приложения под старый 32-битный iPad 2. Нам нужно поднять легковесный консольный тулчейн Theos, подсунуть ему заголовочные файлы старой iOS 9.3 SDK и убедиться, что мы можем нативно компилировать код под `armv7` прямо из терминала.

* **Входные данные:**
  - Mac M4 (Apple Silicon, macOS 14/15/Sonoma/Sequoia).
  - Установленный `Homebrew` и Xcode Command Line Tools (`xcode-select --install`).

* **Выходные данные (DoD):**
  - Папка `~/theos` установлена и добавлена в `$PATH`.
  - В `$THEOS/sdks/` лежит рабочий SDK с поддержкой `armv7` (например, `iPhoneOS9.3.sdk` или `iPhoneOS10.3.sdk`).
  - Минимальный проект «Hello World» собирается командой `make package` без ошибок.
  - Утилита `file` подтверждает тип бинарника: `Mach-O executable arm_v7`.

* **Пошаговая инструкция для разработчика:**
  1. Установить зависимости сборки через Homebrew:
     ```bash
     brew install ldid dpkg
     ```
  2. Склонировать репозиторий Theos:
     ```bash
     git clone --recursive https://github.com/theos/theos.git ~/theos
     ```
  3. Прописать в `~/.zshrc`:
     ```bash
     export THEOS=~/theos
     export PATH=$THEOS/bin:$PATH
     ```
  4. Скачать заголовочный SDK старой iOS (с поддержкой архитектуры `armv7`) и положить в `$THEOS/sdks/`.
  5. Создать в корне проекта базовый `Makefile`:
     ```makefile
     TARGET := iphone:clang:latest:9.3
     ARCHS := armv7
     
     include $(THEOS)/makefiles/common.mk
     
     APPLICATION_NAME = RetroReader
     RetroReader_FILES = src/main.m src/Core/AppDelegate.m
     RetroReader_FRAMEWORKS = UIKit Foundation CoreGraphics
     RetroReader_CFLAGS = -fobjc-arc
     
     include $(THEOS_MAKE_PATH)/application.mk
     ```
  6. Создать файл `control`:
     ```text
     Package: com.retroread.app
     Name: RetroReader
     Depends: 
     Version: 0.1.0
     Architecture: iphoneos-arm
     Description: Offline EPUB reader with instant dictionary for iPad 2
     Maintainer: DevTeam
     Author: DevTeam
     Section: Utilities
     ```

* **Критерии приемки:**
  - [ ] Вызов `make clean && make` отрабатывает с кодом возврата `0`.
  - [ ] Команда `file .theos/obj/debug/RetroReader.app/RetroReader` выдает строку, содержащую `arm_v7`.

---

### [TASK-1.2] Подготовка тестового стенда на iPad 2 (Phoenix + SSH + автоматический деплой)

* **Простыми словами:**  
  Чтобы не подписывать приложение сертификатами Apple каждые 7 дней и не тыкать кабель для каждой правки строчки кода, мы делаем iPad удобным для разработчика: ставим полупривязанный джейлбрейк, включаем SSH и настраиваем деплой по Wi-Fi. Написал код -> нажал в терминале `make install` -> приложение уже открыто на планшете.

* **Входные данные:**
  - Планшет iPad 2 на iOS 9.3.5, подключенный к той же Wi-Fi сети, что и Mac.
  - Кабель 30-pin -> USB для первичной прошивки.
  - Скачанный `Phoenix4.ipa` и утилита Sideloadly на Mac.

* **Выходные данные (DoD):**
  - На iPad установлены Cydia, `OpenSSH` и `AppSync Unified`.
  - С Mac можно зайти на iPad по SSH без пароля: `ssh root@<IP_АЙПАДА>`.
  - Команда `make install` из терминала Mac автоматически собирает проект, копирует `.deb` на iPad, устанавливает его и делает респринг/запуск приложения.

* **Пошаговая инструкция для разработчика:**
  1. Запустить Sideloadly на Mac, перетащить `Phoenix4.ipa`, указать свой Apple ID, нажать «Start».
  2. На iPad зайти в *Настройки -> Основные -> Управление устройством*, нажать «Доверять».
  3. Открыть приложение Phoenix, нажать «Prepare For Jailbreak» -> «Accept» -> «Proceed with Jailbreak» -> «Begin Installation» -> «Use Provided Offsets».
  4. После перезагрузки открыть появившуюся Cydia.
  5. В Cydia установить:
     - Пакет `OpenSSH` (из стандартного репозитория).
     - Добавить репозиторий `https://cydia.akemi.ai/` и установить `AppSync Unified`.
  6. На Mac сгенерировать SSH-ключ (если нет) и скопировать его на iPad:
     ```bash
     ssh-copy-id root@<IP_АДРЕС_АЙПАДА>
     # Стандартный пароль от рута на iOS: alpine
     ```
  7. Добавить IP планшета в переменные окружения Mac или в `Makefile`:
     ```makefile
     THEOS_DEVICE_IP = 192.168.1.XXX
     THEOS_DEVICE_PORT = 22
     ```

* **Критерии приемки:**
  - [ ] Выполняется `make package install`.
  - [ ] На экране iPad появляется иконка `RetroReader` и открывается чистый белый экран с надписью «Hello iPad 2».

---

## MILESTONE 2: Офлайн-словарь и морфология (NLP Engine)

---

### [TASK-2.1] Генератор офлайн-базы SQLite на Mac (Словарь Мюллера / FreeDict)

* **Простыми словами:**  
  Нам нужен компактный англо-русский словарь, который можно положить внутрь приложения. На Mac пишем Python-скрипт, который скачивает текстовый словарь (например, Мюллера), чистит мусор, раскладывает по полочкам (слово, транскрипция, часть речи, перевод) и собирает в быстрый файл `dictionary.sqlite` с индексом.

* **Входные данные:**
  - Исходный открытый текстовый файл англо-русского словаря (например, Mueller24.txt или словарная база FreeDict/Wiktionary в формате TSV).

* **Выходные данные (DoD):**
  - Готовый скрипт `tools/dict_builder/build_dict.py`.
  - Сгенерированный файл `resources/dictionary.sqlite` размером до 20 МБ.
  - База содержит не менее 45 000 уникальных английских слов с корректным индексом.

* **Схема базы данных SQLite:**
  ```sql
  CREATE TABLE words (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      word TEXT NOT NULL COLLATE NOCASE,
      transcription TEXT,
      pos TEXT,
      translation TEXT NOT NULL
  );
  
  CREATE UNIQUE INDEX idx_word_nocase ON words(word COLLATE NOCASE);
  ```

* **Требования к скрипту `build_dict.py`:**
  - Входной аргумент: путь к исходному файлу словаря.
  - Очистка: обрезать пробелы, привести ключи к lowercase, отфильтровать пустые строки и спецсимволы разметки.
  - Оптимизация SQLite:
    - Выполнять вставку одной транзакцией (`BEGIN TRANSACTION` ... `COMMIT`).
    - Выполнить `VACUUM;` и `ANALYZE;` в конце.
    - Установить `PRAGMA page_size = 4096;` (оптимально для чтения на старой памяти iOS).

* **Критерии приемки:**
  - [ ] Запуск `python3 tools/dict_builder/build_dict.py` без ошибок создает `resources/dictionary.sqlite`.
  - [ ] Проверочный SQL-запрос `SELECT translation FROM words WHERE word = 'apple';` возвращает «яблоко» менее чем за 5 мс.

---

### [TASK-2.2] Сервис поиска и лемматизации `RRDictionaryService` (Objective-C)

* **Простыми словами:**  
  Когда юзер тапает по слову *"swimming"* или *"knives"*, в словаре их нет — там есть инфинитивы *"swim"* и *"knife"*. Этот модуль должен:
  1. Нормализовать слово встроенным в iOS 9 системным лемматизатором `NSLinguisticTagger`.
  2. Быстро найти перевод в локальной базе `dictionary.sqlite` через нативный C-интерфейс SQLite.

* **Файлы:**
  - `src/Dictionary/RRWordEntry.h` / `.m`
  - `src/Dictionary/RRDictionaryService.h` / `.m`

* **Спецификация моделей и методов:**

  ```objc
  // RRWordEntry.h
  @interface RRWordEntry : NSObject
  @property (nonatomic, copy) NSString *word;
  @property (nonatomic, copy) NSString *transcription;
  @property (nonatomic, copy) NSString *partOfSpeech;
  @property (nonatomic, copy) NSString *translation;
  @end
  ```

  ```objc
  // RRDictionaryService.h
  @interface RRDictionaryService : NSObject
  
  // Синглтон для доступа к сервису
  + (instancetype)sharedService;
  
  // Открытие базы данных (ленивая инициализация)
  - (BOOL)openDatabaseWithPath:(NSString *)path error:(NSError **)error;
  
  // Приведение слова к нормальной форме (running -> run, children -> child)
  - (NSString *)lemmatizeWord:(NSString *)rawWord;
  
  // Поиск слова (автоматически делает 2 попытки: точное совпадение -> лемма)
  - (RRWordEntry *)lookupWord:(NSString *)word;
  
  // Закрытие базы при выходе/деаллокации
  - (void)closeDatabase;
  
  @end
  ```

* **Детали реализации (`RRDictionaryService.m`):**
  - Использовать `sqlite3_open_v2` с флагом `SQLITE_OPEN_READONLY`.
  - Скомпилировать подготовленный запрос один раз при открытии базы:
    ```c
    sqlite3_prepare_v2(db, "SELECT transcription, pos, translation FROM words WHERE word = ? LIMIT 1;", -1, &stmt, NULL);
    ```
  - Использовать `sqlite3_bind_text` и `sqlite3_step`. Это в 10 раз быстрее, чем каждый раз конструировать строку запроса.
  - В методе `lemmatizeWord:` использовать `NSLinguisticTagger`:
    ```objc
    NSLinguisticTagger *tagger = [[NSLinguisticTagger alloc] initWithTagSchemes:@[NSLinguisticTagSchemeLemma] options:0];
    [tagger setString:cleanWord];
    NSString *lemma = [tagger tagAtIndex:0 scheme:NSLinguisticTagSchemeLemma tokenRange:NULL sentenceRange:NULL];
    ```

* **Критерии приемки:**
  - [ ] Вызов `[[RRDictionaryService sharedService] lookupWord:@"running"]` возвращает `RRWordEntry` с переводом глагола "run" / "бежать".
  - [ ] Время поиска одного слова на реальном iPad 2 составляет менее 10 миллисекунд.
  - [ ] Сервис корректно возвращает `nil`, если слово не найдено, не крашась на спецсимволах.

---

## MILESTONE 3: Парсинг и распаковка EPUB (EPUB Engine)

---

### [TASK-3.1] Легковесная распаковка ZIP-файла книги (`RRZipExtractor`)

* **Простыми словами:**  
  Файл `.epub` — это на самом деле обычный zip-архив с HTML-файлами. Нам нужно распаковать его во временную папку песочницы приложения. Никаких тяжелых сторонних фреймворков брать нельзя — используем проверенный миллионами приложений старый добрый C-модуль `minizip` поверх системного `libz`.

* **Файлы:**
  - `src/Epub/Minizip/unzip.h`, `unzip.c`, `ioapi.h`, `ioapi.c`
  - `src/Epub/RRZipExtractor.h` / `.m`

* **Спецификация класса:**
  ```objc
  // RRZipExtractor.h
  @interface RRZipExtractor : NSObject
  
  // Распаковывает zip-архив по filePath в указанную папку destinationPath.
  // Возвращает YES в случае успеха, NO при ошибке.
  + (BOOL)unzipFileAtPath:(NSString *)filePath 
            toDestination:(NSString *)destinationPath 
                    error:(NSError **)error;
  
  // Возвращает путь к кэш-директории книги (по хешу пути файла)
  + (NSString *)cacheDirectoryForBookPath:(NSString *)filePath;
  
  @end
  ```

* **Детали реализации:**
  - Использовать функции `unzOpen64`, `unzGoToFirstFile`, `unzGetCurrentFileInfo64`, `unzOpenCurrentFile`, `unzReadCurrentFile`, `unzCloseCurrentFile`.
  - Буфер чтения: 8192 байта (8 КБ) — чтобы не забивать оперативную память.
  - Не распаковывать заново, если папка с распакованной книгой уже существует в `Library/Caches/Books/<hash>/`.

* **Критерии приемки:**
  - [ ] Метод `unzipFileAtPath:toDestination:error:` успешно распаковывает тестовый `sample.epub`.
  - [ ] В целевой папке появляются файлы `META-INF/container.xml` и папка с главами.

---

### [TASK-3.2] Парсинг структуры книги (Container, OPF, Spine)

* **Простыми словами:**  
  Внутри EPUB есть файл `container.xml`, который говорит, где лежит манифест книги (`content.opf`). А в `content.opf` прописано: как книга называется, кто автор и в каком порядке читать HTML-главы (список `spine`). Нам нужно распарсить эти XML и собрать готовую модель книги для читалки.

* **Файлы:**
  - `src/Epub/RRBookModel.h` / `.m`
  - `src/Epub/RRChapterModel.h` / `.m`
  - `src/Epub/RREpubParser.h` / `.m`

* **Спецификация моделей:**
  ```objc
  // RRChapterModel.h
  @interface RRChapterModel : NSObject
  @property (nonatomic, copy) NSString *chapterId;
  @property (nonatomic, copy) NSString *title;
  @property (nonatomic, copy) NSString *relativeHtmlPath; // путь к файлу главы относительно папки книги
  @property (nonatomic, assign) NSInteger orderIndex;
  @end
  ```

  ```objc
  // RRBookModel.h
  @interface RRBookModel : NSObject
  @property (nonatomic, copy) NSString *title;
  @property (nonatomic, copy) NSString *author;
  @property (nonatomic, copy) NSString *baseFolderPath; // абсолютный путь к распакованной папке
  @property (nonatomic, strong) NSArray<RRChapterModel *> *chapters; // упорядоченный список глав
  @end
  ```

  ```objc
  // RREpubParser.h
  @interface RREpubParser : NSObject
  
  // Принимает путь к исходному файлу .epub, распаковывает (если нужно) и возвращает модель книги
  + (RRBookModel *)parseEpubAtPath:(NSString *)epubFilePath error:(NSError **)error;
  
  @end
  ```

* **Детали реализации:**
  - Парсинг XML выполнять через системный потоковый `NSXMLParser` с делегатом `NSXMLParserDelegate`.
  - Шаг 1: Парсим `META-INF/container.xml`, ищем тег `<rootfile full-path="..."/>`.
  - Шаг 2: Открываем найденный `.opf` файл.
  - Шаг 3: Собираем словарь манифеста: `<manifest>` -> сопоставление `id` и `href`.
  - Шаг 4: Читаем `<spine>` -> массив `itemref idref="..."`, по этим ID из манифеста достаем правильный порядок HTML-файлов глав.

* **Критерии приемки:**
  - [ ] Парсинг `sample.epub` возвращает объект `RRBookModel`.
  - [ ] Поле `title` книги заполнено корректно.
  - [ ] Массив `chapters` содержит корректные пути к реальным существующим HTML-файлам на диске.

---

## MILESTONE 4: Читалка и перехват кликов (UIWebView + JS Bridge)

---

### [TASK-4.1] Постраничный просмотрщик на базе UIWebView (`RRReaderViewController`)

* **Простыми словами:**  
  Делаем экран, на котором отображается текст книги. Чтобы это выглядело как настоящая книга, а не бесконечная веб-страница со скроллом, мы используем полноэкранный `UIWebView` и CSS-колонки. Текст разбивается на страницы размером с экран iPad (1024x768). Свайп влево/вправо плавно сдвигает страницу.

* **Файлы:**
  - `src/Reader/RRReaderViewController.h` / `.m`
  - `src/Reader/Assets/reader_style.css`

* **Стили страницы (`reader_style.css`):**
  ```css
  html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #F8F5EE; /* Мягкий бумажный фон */
      color: #222222;
  }
  
  #content {
      position: absolute;
      top: 40px;
      left: 50px;
      right: 50px;
      bottom: 40px;
      height: calc(100% - 80px);
      -webkit-column-width: 924px;
      -webkit-column-gap: 100px;
      -webkit-column-fill: auto;
      font-family: "Georgia", serif;
      font-size: 21px;
      line-height: 1.6;
      text-align: justify;
      -webkit-touch-callout: none;
      -webkit-user-select: none; /* Запрещаем системное синее выделение */
  }
  
  img {
      max-width: 100%;
      height: auto;
  }
  ```

* **Спецификация контроллера:**
  ```objc
  // RRReaderViewController.h
  @class RRBookModel;
  
  @interface RRReaderViewController : UIViewController <UIWebViewDelegate>
  
  @property (nonatomic, strong) RRBookModel *book;
  @property (nonatomic, assign) NSInteger currentChapterIndex;
  @property (nonatomic, assign) NSInteger currentPageIndex;
  
  - (instancetype)initWithBook:(RRBookModel *)book;
  - (void)loadChapterAtIndex:(NSInteger)chapterIndex;
  - (void)nextPage;
  - (void)prevPage;
  
  @end
  ```

* **Детали реализации:**
  - В `viewDidLoad` создать `UIWebView`, прикрепить к краям экрана (`autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight`).
  - Отключить лишнее:
    ```objc
    self.webView.scrollView.bounces = NO;
    self.webView.scrollView.scrollEnabled = NO;
    self.webView.dataDetectorTypes = UIDataDetectorTypeNone;
    ```
  - Листание страниц через JavaScript:
    ```objc
    NSString *js = [NSString stringWithFormat:@"window.scrollTo(%ld * 1024, 0);", (long)self.currentPageIndex];
    [self.webView stringByEvaluatingJavaScriptFromString:js];
    ```
  - Добавить `UISwipeGestureRecognizer` (влево -> `nextPage`, вправо -> `prevPage`).

* **Критерии приемки:**
  - [ ] Глава EPUB открывается на весь экран iPad с красивыми полями.
  - [ ] Свайпы листают страницы без лагов и дерганий.
  - [ ] При достижении конца главы автоматически подгружается следующая глава.

---

### [TASK-4.2] Интерактивный JS-мост для клика по словам (`reader_bridge.js`)

* **Простыми словами:**  
  Юзер пальцем тыкает в любое английское слово на странице. Нам нужно в браузере понять: какое именно слово нажал юзер, вырезать его, получить его точные координаты `(x, y, width, height)` на экране iPad и моментально передать это в нативный код Objective-C.

* **Файлы:**
  - `src/Reader/Assets/reader_bridge.js`
  - Доработка `RRReaderViewController.m`

* **Спецификация JavaScript (`reader_bridge.js`):**
  ```javascript
  (function() {
      document.addEventListener('click', function(e) {
          // 1. Получаем диапазон текста под точкой клика
          var range = document.caretRangeFromPoint(e.clientX, e.clientY);
          if (!range) return;
          
          // 2. Расширяем диапазон до границы слова
          range.expand('word');
          var rawWord = range.toString().trim();
          if (!rawWord || rawWord.length === 0) return;
          
          // 3. Очищаем от знаков пунктуации по краям
          var cleanWord = rawWord.replace(/^[.,\/#!$%\^&\*;:{}=\-_`~()"'“”‘’]+|[.,\/#!$%\^&\*;:{}=\-_`~()"'“”‘’]+$/g, "");
          if (cleanWord.length === 0) return;
          
          // 4. Получаем экранный прямоугольник слова
          var rect = range.getBoundingClientRect();
          
          // 5. Отправляем в Objective-C через кастомный URI-схем
          var url = 'reader-bridge://wordTap?' + 
                    'word=' + encodeURIComponent(cleanWord) +
                    '&x=' + rect.left +
                    '&y=' + rect.top +
                    '&w=' + rect.width +
                    '&h=' + rect.height;
          
          window.location.href = url;
      }, false);
  })();
  ```

* **Перехват в Objective-C (`RRReaderViewController.m`):**
  - Реализовать метод делегата:
    ```objc
    - (BOOL)webView:(UIWebView *)webView shouldStartLoadWithRequest:(NSURLRequest *)request navigationType:(UIWebViewNavigationType)navigationType {
        NSURL *url = request.URL;
        if ([url.scheme isEqualToString:@"reader-bridge"]) {
            if ([url.host isEqualToString:@"wordTap"]) {
                [self handleWordTapFromURL:url];
                return NO; // Отменяем загрузку страницы в webview
            }
        }
        return YES;
    }
    ```
  - Метод `handleWordTapFromURL:` парсит query-параметры `word`, `x`, `y`, `w`, `h` и формирует структуру `CGRect`.

* **Критерии приемки:**
  - [ ] При тапе по слову в консоли планшета появляется лог: `Tapped word: <word>, Rect: {x, y, w, h}`.
  - [ ] Пунктуация (запятые, точки, кавычки) корректно отсекается.
  - [ ] Тап по пустому месту или картинке не вызывает ложных срабатываний.

---

## MILESTONE 5: Всплывающий бабл с переводом (Popover UI)

---

### [TASK-5.1] Контроллер всплывающего окна перевода (`RRTranslationViewController`)

* **Простыми словами:**  
  Верстаем карточку, которая будет показываться внутри всплывающего пузырика. В ней должно быть: само слово крупным шрифтом, транскрипция, бейдж части речи (существительное, глагол и т.д.) и аккуратный блок с вариантами перевода на русском.

* **Файлы:**
  - `src/Popover/RRTranslationViewController.h` / `.m`

* **Спецификация класса:**
  ```objc
  // RRTranslationViewController.h
  @class RRWordEntry;
  
  @interface RRTranslationViewController : UIViewController
  
  @property (nonatomic, strong) RRWordEntry *wordEntry;
  
  // Конструктор с инициализацией словарной статьей
  - (instancetype)initWithWordEntry:(RRWordEntry *)entry;
  
  @end
  ```

* **Детали верстки интерфейса:**
  - Задать фиксированный размер карточки:
    ```objc
    self.preferredContentSize = CGSizeMake(300, 160);
    ```
  - Элементы UI:
    - `UILabel *lblWord`: шрифт системный жирный 20pt, цвет `#1A1A1A`.
    - `UILabel *lblTranscription`: шрифт 14pt курсив, цвет `#666666` (например, `[æpl]`).
    - `UILabel *lblPartOfSpeech`: бейдж со скругленными краями (например, `noun`).
    - `UITextView *txtTranslation`: прокручиваемый текст перевода, шрифт 16pt, цвет `#333333`, `editable = NO`.
    - Если слово не найдено в базе — отображается аккуратное сообщение *"Перевод не найден"*.

* **Критерии приемки:**
  - [ ] Контроллер корректно отображает слово, транскрипцию и перевод.
  - [ ] Длинные статьи перевода аккуратно прокручиваются внутри текстового поля.

---

### [TASK-5.2] Интеграция `UIPopoverPresentationController` с привязкой к слову

* **Простыми словами:**  
  Связываем все воедино: при клике на слово берем его координаты, запрашиваем перевод в словаре, создаем карточку перевода и показываем нативный бабл со стрелочкой, указывающей прямо на слово в книге.

* **Файлы:**
  - Доработка `RRReaderViewController.m`

* **Детали реализации:**
  ```objc
  - (void)showTranslationForWord:(NSString *)word targetRect:(CGRect)rect {
      // 1. Поиск перевода в SQLite сервисе
      RRWordEntry *entry = [[RRDictionaryService sharedService] lookupWord:word];
      if (!entry) {
          entry = [[RRWordEntry alloc] init];
          entry.word = word;
          entry.translation = @"Перевод не найден в офлайн-словаре";
      }
      
      // 2. Создаем контроллер попапа
      RRTranslationViewController *popoverVC = [[RRTranslationViewController alloc] initWithWordEntry:entry];
      popoverVC.modalPresentationStyle = UIModalPresentationPopover;
      
      // 3. Настраиваем привязку стрелочки бабла
      UIPopoverPresentationController *popPresenter = popoverVC.popoverPresentationController;
      popPresenter.sourceView = self.webView;
      popPresenter.sourceRect = rect;
      popPresenter.permittedArrowDirections = UIPopoverArrowDirectionUp | UIPopoverArrowDirectionDown;
      popPresenter.delegate = self;
      
      // 4. Показываем попап
      [self presentViewController:popoverVC animated:YES completion:nil];
  }
  ```

* **Критерии приемки:**
  - [ ] При тапе по слову бабл появляется ровно над (или под) словом со стрелочкой, указывающей на буквы.
  - [ ] Тап вне бабла закрывает всплывающее окно.
  - [ ] При быстром тапе по другому слову старый бабл плавно заменяется новым.

---

## MILESTONE 6: Защита от утечек памяти (512 MB RAM) и релизная сборка

---

### [TASK-6.1] Управление памятью под лимиты iPad 2 (Jetsam Protection)

* **Простыми словами:**  
  WebKit и UIWebView на старых версиях iOS имеют неприятное свойство накапливать кэш картинок и отрисованных страниц в RAM. У нас всего 512 МБ памяти, поэтому нужно защитить приложение от внезапных вылетов при чтении больших книг.

* **Файлы:**
  - `src/Reader/RRReaderViewController.m`
  - `src/Core/AppDelegate.m`

* **Детали реализации:**
  1. Реализовать обработку системного предупреждения о памяти:
     ```objc
     - (void)didReceiveMemoryWarning {
         [super didReceiveMemoryWarning];
         // Сбрасываем кэш URL-сессий и WebKit
         [[NSURLCache sharedURLCache] removeAllCachedResponses];
     }
     ```
  2. Не держать в памяти распарсенные HTML всех глав сразу: в `UIWebView` загружается **только текущая глава**. При переходе на другую главу предыдущая выгружается из DOM.
  3. Очищать WebView при сворачивании приложения в фон.

* **Критерии приемки:**
  - [ ] При непрерывном чтении 20 глав книги подряд потребление памяти приложения (Resident Memory) не превышает 45–60 МБ.
  - [ ] Приложение не вылетает с логом `Jetsam / EXC_RESOURCE` в краш-логах планшета.

---

### [TASK-6.2] Добавление демо-ресурсов и сборка релизного пакета

* **Простыми словами:**  
  Кладем внутрь приложения бесплатную книгу (например, «Алису в Стране чудес» на английском языке) и файл базы данных словаря. Собираем финальный установочный `.deb` пакет и `.ipa` для планшета.

* **Файлы:**
  - `resources/sample.epub`
  - `resources/dictionary.sqlite`
  - Обновление `Makefile` для включения ресурсов в `.app` бандл.

* **Строка сборки в Makefile:**
  ```makefile
  RetroReader_RESOURCE_DIRS = resources
  ```

* **Критерии приемки:**
  - [ ] Выполняется чистая сборка: `make clean && make package`.
  - [ ] Готовый `.deb` устанавливается на iPad 2.
  - [ ] При первом запуске сразу открывается книга, любое слово переводится по нажатию без интернета.

---

## Чеклист готовности к работе

- [ ] Все задачи оцифрованы в `docs/TASKS_SPEC.md`.
- [ ] Готов план компиляции базы данных словаря.
- [ ] Готова структура исходного кода.

Переходим к первому шагу реализации: генерации словаря и созданию базовой файловой структуры проекта.
