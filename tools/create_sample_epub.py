#!/usr/bin/env python3
"""
Создание валидного sample.epub с первыми двумя главами 'Alice in Wonderland'
для тестирования читалки RetroReader.
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
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
        <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
    </manifest>
    <spine toc="ncx">
        <itemref idref="chapter1"/>
        <itemref idref="chapter2"/>
    </spine>
</package>
"""

TOC_NCX = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:12345-alice-in-wonderland"/>
    </head>
    <docTitle>
        <text>Alice's Adventures in Wonderland</text>
    </docTitle>
    <navMap>
        <navPoint id="navPoint-1" playOrder="1">
            <navLabel><text>Chapter I: Down the Rabbit-Hole</text></navLabel>
            <content src="chapter1.xhtml"/>
        </navPoint>
        <navPoint id="navPoint-2" playOrder="2">
            <navLabel><text>Chapter II: The Pool of Tears</text></navLabel>
            <content src="chapter2.xhtml"/>
        </navPoint>
    </navMap>
</ncx>
"""

CHAPTER1_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter I</title>
</head>
<body>
    <h1>CHAPTER I</h1>
    <h2>Down the Rabbit-Hole</h2>
    <p>Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice 'without pictures or conversations?'</p>
    <p>So she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.</p>
    <p>There was nothing so very remarkable in that; nor did Alice think it so very much out of the way to hear the Rabbit say to itself, 'Oh dear! Oh dear! I shall be late!' (when she thought it over afterwards, it occurred to her that she ought to have wondered at this, but at the time it all seemed quite natural); but when the Rabbit actually took a watch out of its waistcoat-pocket, and looked at it, and then hurried on, Alice started to her feet, for it flashed across her mind that she had never before seen a rabbit with either a waistcoat-pocket, or a watch to take out of it, and burning with curiosity, she ran across the field after it, and fortunately was just in time to see it pop down a large rabbit-hole under the hedge.</p>
    <p>In another moment down went Alice after it, never once considering how in the world she was to get out again.</p>
    <p>The rabbit-hole went straight on like a tunnel for some way, and then dipped suddenly down, so suddenly that Alice had not a moment to think about stopping herself before she found herself falling down a very deep well.</p>
    <p>Either the well was very deep, or she fell very slowly, for she had plenty of time as she went down to look about her and to wonder what was going to happen next. First, she tried to look down and make out what she was coming to, but it was too dark to see anything; then she looked at the sides of the well, and noticed that they were filled with cupboards and book-shelves; here and there she saw maps and pictures hung upon pegs. She took down a jar from one of the shelves as she passed; it was labelled 'ORANGE MARMALADE', but to her great disappointment it was empty: she did not like to drop the jar for fear of killing somebody, so managed to put it into one of the cupboards as she fell past it.</p>
</body>
</html>
"""

CHAPTER2_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter II</title>
</head>
<body>
    <h1>CHAPTER II</h1>
    <h2>The Pool of Tears</h2>
    <p>'Curiouser and curiouser!' cried Alice (she was so much surprised, that for the moment she quite forgot how to speak good English); 'now I'm opening out like the largest telescope that ever was! Good-bye, feet!' (for when she looked down at her feet, they seemed to be almost out of sight, they were getting so far off). 'Oh, my poor little feet, I wonder who will put on your shoes and stockings for you now, dears? I'm sure I shan't be able!'</p>
    <p>Just at this moment her head struck against the roof of the hall: in fact she was now more than nine feet high, and she at once took up the little golden key and hurried off to the garden door.</p>
</body>
</html>
"""

def create_epub():
    os.makedirs(os.path.dirname(OUTPUT_EPUB), exist_ok=True)
    with zipfile.ZipFile(OUTPUT_EPUB, 'w') as z:
        # 1. mimetype (должен быть первым и несжатым)
        z.writestr('mimetype', MIMETYPE, compress_type=zipfile.ZIP_STORED)
        
        # 2. container.xml
        z.writestr('META-INF/container.xml', CONTAINER_XML, compress_type=zipfile.ZIP_DEFLATED)
        
        # 3. content.opf & toc.ncx
        z.writestr('OEBPS/content.opf', CONTENT_OPF, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/toc.ncx', TOC_NCX, compress_type=zipfile.ZIP_DEFLATED)
        
        # 4. chapters
        z.writestr('OEBPS/chapter1.xhtml', CHAPTER1_XHTML, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/chapter2.xhtml', CHAPTER2_XHTML, compress_type=zipfile.ZIP_DEFLATED)
        
    print(f"[OK] Создан sample.epub: {OUTPUT_EPUB} ({os.path.getsize(OUTPUT_EPUB)} bytes)")

if __name__ == '__main__':
    create_epub()
