/**
 * RetroReader JavaScript Bridge для UIWebView на iOS 9.3.5
 * 1. Отслеживает тапы по словам через caretRangeFromPoint.
 * 2. Вычисляет координаты слова на экране iPad.
 * 3. Отправляет событие в Objective-C через кастомный URI-схем.
 * 4. Управляет горизонтальной пагинацией страниц.
 */

(function() {
    // Предотвращаем повторную инициализацию
    if (window.RRBridgeInitialized) return;
    window.RRBridgeInitialized = true;

    // Символы пунктуации для очистки слова
    var PUNCT_REGEX = /^[.,\/#!$%\^&\*;:{}=\-_`~()"'“”‘’«»—…]+|[.,\/#!$%\^&\*;:{}=\-_`~()"'“”‘’«»—…]+$/g;

    document.addEventListener('click', function(e) {
        // 1. Находим позицию в тексте под точкой клика
        var range = null;
        if (document.caretRangeFromPoint) {
            range = document.caretRangeFromPoint(e.clientX, e.clientY);
        }
        if (!range) return;

        // 2. Расширяем диапазон до границы слова
        range.expand('word');
        var rawText = range.toString().trim();
        if (!rawText || rawText.length === 0) return;

        // 3. Очищаем краевую пунктуацию
        var cleanWord = rawText.replace(PUNCT_REGEX, "");
        if (cleanWord.length === 0) return;

        // 4. Получаем координаты прямоугольника слова на экране
        var rect = range.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        // 5. Передаем в Objective-C
        var bridgeUrl = 'reader-bridge://wordTap?' +
                        'word=' + encodeURIComponent(cleanWord) +
                        '&x=' + Math.round(rect.left) +
                        '&y=' + Math.round(rect.top) +
                        '&w=' + Math.round(rect.width) +
                        '&h=' + Math.round(rect.height);

        window.location.href = bridgeUrl;
    }, false);

    // Функции управления пагинацией
    window.RRGetTotalPages = function() {
        var container = document.getElementById('book-container') || document.body;
        var totalWidth = container.scrollWidth;
        var pageWidth = window.innerWidth || 1024;
        return Math.max(1, Math.ceil(totalWidth / pageWidth));
    };

    window.RRScrollToPage = function(pageIndex) {
        var pageWidth = window.innerWidth || 1024;
        window.scrollTo(pageIndex * pageWidth, 0);
    };
})();
