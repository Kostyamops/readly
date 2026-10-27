#!/usr/bin/env python3
"""
Создание тестовой книги sample.epub (Alice in Wonderland) для RetroReader.
"""

import os
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
OUTPUT_EPUB = os.path.join(PROJECT_ROOT, "resources", "sample.epub")

MIMETYPE = "application/epub+zip"

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>
"""

CONTENT_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>Alice's Adventures in Wonderland</dc:title>
        <dc:creator opf:role="aut">Lewis Carroll</dc:creator>
        <dc:language>en</dc:language>
        <dc:identifier id="BookID">urn:uuid:12345-alice-in-wonderland</dc:identifier>
    </metadata>
    <manifest>
        <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
        <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
    </manifest>
    <spine>
        <itemref idref="chapter1"/>
        <itemref idref="chapter2"/>
    </spine>
</package>
"""

CHAPTER1_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter I</title></head>
<body>
    <h1>CHAPTER I</h1>
    <h2>Down the Rabbit-Hole</h2>
    <p>Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice 'without pictures or conversations?'</p>
    <p>So she was considering in her own mind, whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.</p>
</body>
</html>
"""

CHAPTER2_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter II</title></head>
<body>
    <h1>CHAPTER II</h1>
    <h2>The Pool of Tears</h2>
    <p>'Curiouser and curiouser!' cried Alice (she was so much surprised, that for the moment she quite forgot how to speak good English); 'now I'm opening out like the largest telescope that ever was! Good-bye, feet!'</p>
</body>
</html>
"""

def create_epub():
    os.makedirs(os.path.dirname(OUTPUT_EPUB), exist_ok=True)
    with zipfile.ZipFile(OUTPUT_EPUB, 'w') as z:
        z.writestr('mimetype', MIMETYPE, compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', CONTAINER_XML, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/content.opf', CONTENT_OPF, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/chapter1.xhtml', CHAPTER1_XHTML, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/chapter2.xhtml', CHAPTER2_XHTML, compress_type=zipfile.ZIP_DEFLATED)
    print(f"[OK] sample.epub создан: {OUTPUT_EPUB}")

if __name__ == '__main__':
    create_epub()
