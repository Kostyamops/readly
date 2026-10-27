/**
 * RetroReader JavaScript Bridge для UIWebView на iOS 9.3.5
 * 1. Отслеживает тапы по словам через caretRangeFromPoint.
 * 2. Вычисляет координаты слова на экране iPad.
 * 3. Отправляет событие в Objective-C через кастомный URI-схем reader-bridge://wordTap и window.RRGetWordAt.
 * 4. Управляет горизонтальной пагинацией страниц.
 */

(function() {
    if (window.RRBridgeInitialized) return;
    window.RRBridgeInitialized = true;

    var PUNCT_REGEX = /^[.,\/#!$%\^&\*;:{}=\-_`~()"'“”‘’«»—…]+|[.,\/#!$%\^&\*;:{}=\-_`~()"'“”‘’«»—…]+$/g;

    function sendBridgeMessage(url) {
        var iframe = document.createElement('iframe');
        iframe.setAttribute('src', url);
        iframe.setAttribute('style', 'display:none;position:absolute;top:-9999px;');
        document.documentElement.appendChild(iframe);
        setTimeout(function() {
            if (iframe.parentNode) {
                iframe.parentNode.removeChild(iframe);
            }
        }, 150);
    }

    function isWordChar(c) {
        return /[a-zA-Z0-9\u0400-\u04FF\u00C0-\u017F\'\u2019]/.test(c);
    }

    function getWordAt(clientX, clientY) {
        if (!document.caretRangeFromPoint) return "";

        var range = document.caretRangeFromPoint(clientX, clientY);
        // Небольшой jitter fallback (±5px), если тап пришелся между буквами или строками
        if (!range) {
            var deltas = [[0, -5], [0, 5], [-5, 0], [5, 0]];
            for (var i = 0; i < deltas.length; i++) {
                range = document.caretRangeFromPoint(clientX + deltas[i][0], clientY + deltas[i][1]);
                if (range) break;
            }
        }
        if (!range) return "";

        var cleanWord = "";
        var rect = null;

        // 1. Попытка использовать нативный WebKit expand('word')
        var expandedNative = false;
        if (typeof range.expand === 'function') {
            try {
                range.expand('word');
                var raw = range.toString().trim();
                cleanWord = raw.replace(PUNCT_REGEX, "");
                rect = range.getBoundingClientRect();
                if (cleanWord.length > 0 && rect && rect.width > 0) {
                    expandedNative = true;
                }
            } catch(e) {}
        }

        // 2. Надежный fallback по границам текстового узла DOM
        if (!expandedNative) {
            var node = range.startContainer;
            var offset = range.startOffset;
            if (node && node.nodeType === 1 && node.childNodes.length > 0) {
                var child = node.childNodes[Math.min(offset, node.childNodes.length - 1)];
                if (child && child.nodeType === 3) {
                    node = child;
                    offset = 0;
                }
            }
            if (!node || node.nodeType !== 3 || !node.textContent) return "";

            var text = node.textContent;
            var start = Math.min(offset, text.length);
            var end = Math.min(offset, text.length);

            while (start > 0 && isWordChar(text.charAt(start - 1))) {
                start--;
            }
            while (end < text.length && isWordChar(text.charAt(end))) {
                end++;
            }

            cleanWord = text.substring(start, end).trim().replace(PUNCT_REGEX, "");
            if (cleanWord.length === 0) return "";

            var wordRange = document.createRange();
            wordRange.setStart(node, start);
            wordRange.setEnd(node, end);
            rect = wordRange.getBoundingClientRect();
        }

        // Немедленно снимаем выделение, чтобы не возникало синих маркеров
        if (window.getSelection) {
            try {
                window.getSelection().removeAllRanges();
            } catch(e) {}
        }

        if (!cleanWord || cleanWord.length === 0) return "";

        var x = (rect && rect.width > 0) ? Math.round(rect.left) : clientX;
        var y = (rect && rect.height > 0) ? Math.round(rect.top) : clientY;
        var w = (rect && rect.width > 0) ? Math.round(rect.width) : 40;
        var h = (rect && rect.height > 0) ? Math.round(rect.height) : 20;

        return JSON.stringify({
            word: cleanWord,
            x: x,
            y: y,
            w: w,
            h: h
        });
    }

    function handleTapAt(clientX, clientY) {
        var jsonStr = getWordAt(clientX, clientY);
        if (!jsonStr) return;

        try {
            var data = JSON.parse(jsonStr);
            if (!data.word) return;

            var bridgeUrl = 'reader-bridge://wordTap?' +
                            'word=' + encodeURIComponent(data.word) +
                            '&x=' + data.x +
                            '&y=' + data.y +
                            '&w=' + data.w +
                            '&h=' + data.h;

            sendBridgeMessage(bridgeUrl);
        } catch(e) {}
    }

    // Экспорт для нативного вызова из Objective-C (UITapGestureRecognizer и stringByEvaluatingJavaScriptFromString)
    window.RRGetWordAt = getWordAt;
    window.RRHandleTapAt = handleTapAt;

    // Автоматические слушатели touchend/click в DOM отключены в пользу нативного UITapGestureRecognizer
    // в RRReaderViewController, который мгновенно вызывает window.RRGetWordAt(x, y) без задержек WebKit
    // и без двойного срабатывания синтетического click (~350ms).
    // window.RRHandleTapAt и reader-bridge://wordTap сохранены для прямого вызова.

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
