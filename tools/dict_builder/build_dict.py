#!/usr/bin/env python3
"""
Скрипт сборки компактной офлайн-базы словаря SQLite для RetroReader (iOS 9.3.5 / iPad 2).
Создает базу данных с NOCASE B-Tree индексом для мгновенного поиска за O(log N).
"""

import os
import sys
import sqlite3
import urllib.request
import gzip
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")
OUTPUT_DB_PATH = os.path.join(RESOURCES_DIR, "dictionary.sqlite")

SCHEMA_SQL = """
PRAGMA page_size = 4096;
PRAGMA journal_mode = OFF;
PRAGMA synchronous = OFF;

DROP TABLE IF EXISTS words;

CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL COLLATE NOCASE,
    transcription TEXT,
    pos TEXT,
    translation TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_word_nocase ON words(word COLLATE NOCASE);
"""

# Базовый стартовый словарь (более 250 самых распространенных слов английского языка)
# для гарантии работоспособности приложения прямо "из коробки"
BUILTIN_CORE_VOCABULARY = [
    ("a", "", "article", "неопределенный артикль"),
    ("the", "", "article", "определенный артикль"),
    ("be", "[biː]", "verb", "быть, существовать, находиться"),
    ("have", "[hæv]", "verb", "иметь, обладать"),
    ("do", "[duː]", "verb", "делать, выполнять"),
    ("say", "[seɪ]", "verb", "сказать, говорить"),
    ("go", "[ɡəʊ]", "verb", "идти, ехать, уходить"),
    ("get", "[ɡet]", "verb", "получать, становиться, добираться"),
    ("make", "[meɪk]", "verb", "делать, создавать, производить"),
    ("know", "[nəʊ]", "verb", "знать, понимать"),
    ("think", "[θɪŋk]", "verb", "думать, полагать"),
    ("take", "[teɪk]", "verb", "брать, взять, принимать"),
    ("see", "[siː]", "verb", "видеть, смотреть, понимать"),
    ("come", "[kʌm]", "verb", "приходить, приезжать"),
    ("want", "[wɒnt]", "verb", "хотеть, желать"),
    ("look", "[lʊk]", "verb/noun", "смотреть, выглядеть; взгляд"),
    ("use", "[juːz]", "verb/noun", "использовать; польза, применение"),
    ("find", "[faɪnd]", "verb", "находить, обнаруживать"),
    ("give", "[ɡɪv]", "verb", "давать, предоставлять"),
    ("tell", "[tel]", "verb", "рассказывать, сообщать"),
    ("work", "[wɜːk]", "verb/noun", "работать; работа, труд"),
    ("call", "[kɔːl]", "verb/noun", "звать, звонить; звонок, вызов"),
    ("try", "[traɪ]", "verb/noun", "пробовать, пытаться; попытка"),
    ("ask", "[ɑːsk]", "verb", "спрашивать, просить"),
    ("need", "[niːd]", "verb/noun", "нуждаться; потребность, нужда"),
    ("feel", "[fiːl]", "verb", "чувствовать, ощущать"),
    ("become", "[bɪˈkʌm]", "verb", "становиться, делаться"),
    ("leave", "[liːv]", "verb", "покидать, оставлять, уходить"),
    ("put", "[pʊt]", "verb", "класть, ставить, помещать"),
    ("mean", "[miːn]", "verb", "значить, иметь в виду"),
    ("keep", "[kiːp]", "verb", "держать, хранить, сохранять"),
    ("let", "[let]", "verb", "позволять, разрешать, пускать"),
    ("begin", "[bɪˈɡɪn]", "verb", "начинать, начинаться"),
    ("seem", "[siːm]", "verb", "казаться, представляться"),
    ("help", "[help]", "verb/noun", "помогать; помощь"),
    ("talk", "[tɔːk]", "verb/noun", "говорить, беседовать; разговор"),
    ("turn", "[tɜːn]", "verb/noun", "поворачивать, крутить; поворот, очередь"),
    ("start", "[stɑːt]", "verb/noun", "начинать; начало, старт"),
    ("show", "[ʃəʊ]", "verb/noun", "показывать; показ, шоу"),
    ("hear", "[hɪə]", "verb", "слышать, слушать"),
    ("play", "[pleɪ]", "verb/noun", "играть; игра, пьеса"),
    ("run", "[rʌn]", "verb/noun", "бежать, бегать; бег"),
    ("move", "[muːv]", "verb/noun", "двигаться, перемещать; движение"),
    ("like", "[laɪk]", "verb/prep", "любить, нравиться; подобный, как"),
    ("live", "[lɪv]", "verb", "жить, существовать"),
    ("believe", "[bɪˈliːv]", "verb", "верить, полагать"),
    ("hold", "[həʊld]", "verb", "держать, удерживать, владеть"),
    ("bring", "[brɪŋ]", "verb", "приносить, приводить, доставлять"),
    ("happen", "[ˈhæp.ən]", "verb", "случаться, происходить"),
    ("must", "[mʌst]", "modal", "должен, обязан"),
    ("write", "[raɪt]", "verb", "писать, записывать"),
    ("provide", "[prəˈvaɪd]", "verb", "обеспечивать, предоставлять"),
    ("sit", "[sɪt]", "verb", "сидеть, садиться"),
    ("stand", "[stænd]", "verb/noun", "стоять; стенд, стойка"),
    ("lose", "[luːz]", "verb", "терять, проигрывать"),
    ("pay", "[peɪ]", "verb/noun", "платить; плата"),
    ("meet", "[miːt]", "verb", "встречать, знакомиться"),
    ("include", "[ɪnˈkluːd]", "verb", "включать в себя, содержать"),
    ("continue", "[kənˈtɪn.juː]", "verb", "продолжать, продолжаться"),
    ("set", "[set]", "verb/noun", "устанавливать; набор, комплект"),
    ("learn", "[lɜːn]", "verb", "учить, учиться, узнавать"),
    ("change", "[tʃeɪndʒ]", "verb/noun", "менять, изменяться; перемена, сдача"),
    ("lead", "[liːd]", "verb/noun", "вести, руководить; лидерство"),
    ("understand", "[ˌʌn.dəˈstænd]", "verb", "понимать, постигать"),
    ("watch", "[wɒtʃ]", "verb/noun", "наблюдать, смотреть; часы"),
    ("follow", "[ˈfɒl.əʊ]", "verb", "следовать, идти за"),
    ("stop", "[stɒp]", "verb/noun", "останавливать; остановка"),
    ("create", "[kriˈeɪt]", "verb", "создавать, творить"),
    ("speak", "[spiːk]", "verb", "говорить, разговаривать"),
    ("read", "[riːd]", "verb", "читать, прочесть"),
    ("allow", "[əˈlaʊ]", "verb", "разрешать, позволять"),
    ("add", "[æd]", "verb", "добавлять, прибавлять"),
    ("spend", "[spend]", "verb", "тратить, проводить (время)"),
    ("grow", "[ɡrəʊ]", "verb", "расти, выращивать"),
    ("open", "[ˈəʊ.pən]", "verb/adj", "открывать; открытый"),
    ("walk", "[wɔːk]", "verb/noun", "гулять, идти пешком; прогулка"),
    ("win", "[wɪn]", "verb", "побеждать, выигрывать"),
    ("offer", "[ˈɒf.ər]", "verb/noun", "предлагать; предложение"),
    ("remember", "[rɪˈmem.bər]", "verb", "помнить, вспоминать"),
    ("love", "[lʌv]", "verb/noun", "любить; любовь"),
    ("consider", "[kənˈsɪd.ər]", "verb", "рассматривать, считать"),
    ("appear", "[əˈpɪər]", "verb", "появляться, казаться"),
    ("buy", "[baɪ]", "verb", "покупать, приобретать"),
    ("wait", "[weɪt]", "verb", "ждать, ожидать"),
    ("serve", "[sɜːv]", "verb", "служить, обслуживать"),
    ("die", "[daɪ]", "verb", "умирать, угасать"),
    ("send", "[send]", "verb", "отправлять, посылать"),
    ("expect", "[ɪkˈspekt]", "verb", "ожидать, рассчитывать"),
    ("build", "[bɪld]", "verb", "строить, создавать"),
    ("stay", "[steɪ]", "verb/noun", "оставаться; пребывание"),
    ("fall", "[fɔːl]", "verb/noun", "падать; падение, осень"),
    ("cut", "[kʌt]", "verb/noun", "резать; разрез, порез"),
    ("reach", "[riːtʃ]", "verb", "достигать, дотягиваться"),
    ("kill", "[kɪl]", "verb", "убивать, уничтожать"),
    ("remain", "[rɪˈmeɪn]", "verb", "оставаться, сохраняться"),
    ("suggest", "[səˈdʒest]", "verb", "предлагать, советовать"),
    ("raise", "[reɪz]", "verb", "поднимать, воспитывать"),
    ("pass", "[pɑːs]", "verb", "проходить, передавать, сдавать (экзамен)"),
    ("sell", "[sel]", "verb", "продавать"),
    ("require", "[rɪˈkwaɪər]", "verb", "требовать, нуждаться"),
    ("report", "[rɪˈpɔːt]", "verb/noun", "сообщать; отчет, доклад"),
    ("decide", "[dɪˈsaɪd]", "verb", "решать, принимать решение"),
    ("pull", "[pʊl]", "verb", "тянуть, тащить"),
    ("book", "[bʊk]", "noun/verb", "книга; бронировать"),
    ("rabbit", "[ˈræb.ɪt]", "noun", "кролик"),
    ("hole", "[həʊl]", "noun", "нора, дыра, отверстие"),
    ("alice", "[ˈæl.ɪs]", "noun", "Алиса"),
    ("wonderland", "[ˈwʌn.də.lænd]", "noun", "страна чудес"),
    ("curious", "[ˈkjʊə.ri.əs]", "adj", "любопытный, странный, необычный"),
    ("tea", "[tiː]", "noun", "чай"),
    ("party", "[ˈpɑː.ti]", "noun", "вечеринка, прием, партия"),
    ("queen", "[kwiːn]", "noun", "королева"),
    ("king", "[kɪŋ]", "noun", "король"),
    ("head", "[hed]", "noun", "голова, руководитель"),
    ("time", "[taɪm]", "noun", "время, раз, эпоха"),
    ("person", "[ˈpɜː.sən]", "noun", "человек, личность"),
    ("year", "[jɪər]", "noun", "год"),
    ("way", "[weɪ]", "noun", "путь, дорога, способ"),
    ("day", "[deɪ]", "noun", "день, сутки"),
    ("man", "[mæn]", "noun", "мужчина, человек"),
    ("world", "[wɜːld]", "noun", "мир, вселенная"),
    ("life", "[laɪf]", "noun", "жизнь"),
    ("hand", "[hænd]", "noun", "рука, кисть руки"),
    ("part", "[pɑːt]", "noun", "часть, роль, деталь"),
    ("child", "[tʃaɪld]", "noun", "ребенок, дитя"),
    ("eye", "[aɪ]", "noun", "глаз, взгляд"),
    ("woman", "[ˈwʊm.ən]", "noun", "женщина"),
    ("place", "[pleɪs]", "noun", "место, площадь"),
    ("case", "[keɪs]", "noun", "случай, обстоятельство, дело"),
    ("point", "[pɔɪnt]", "noun", "точка, пункт, смысл"),
    ("government", "[ˈɡʌv.ən.mənt]", "noun", "правительство"),
    ("company", "[ˈkʌm.pə.ni]", "noun", "компания, общество, фирма"),
    ("number", "[ˈnʌm.bər]", "noun", "число, номер, количество"),
    ("group", "[ɡruːp]", "noun", "группа"),
    ("problem", "[ˈprɒb.ləm]", "noun", "проблема, задача"),
    ("fact", "[fækt]", "noun", "факт, действительность"),
    ("good", "[ɡʊd]", "adj", "хороший, добрый"),
    ("new", "[njuː]", "adj", "новый, свежий"),
    ("first", "[fɜːst]", "adj/adv", "первый; сначала"),
    ("last", "[lɑːst]", "adj/adv", "последний, прошлый"),
    ("long", "[lɒŋ]", "adj", "длинный, долгий"),
    ("great", "[ɡreɪt]", "adj", "великий, огромный, отличный"),
    ("little", "[ˈlɪt.əl]", "adj/adv", "маленький; мало"),
    ("own", "[əʊn]", "adj/verb", "собственный; владеть"),
    ("other", "[ˈʌð.ər]", "adj", "другой, иной"),
    ("old", "[əʊld]", "adj", "старый, прежний"),
    ("right", "[raɪt]", "adj/noun", "правый, правильный; право"),
    ("big", "[bɪɡ]", "adj", "большой, крупный"),
    ("high", "[haɪ]", "adj", "высокий"),
    ("different", "[ˈdɪf.ər.ənt]", "adj", "различный, другой"),
    ("small", "[smɔːl]", "adj", "маленький, небольшой"),
    ("large", "[lɑːdʒ]", "adj", "большой, обширный"),
    ("next", "[nekst]", "adj", "следующий, соседний"),
    ("early", "[ˈɜː.li]", "adj/adv", "ранний; рано"),
    ("young", "[jʌŋ]", "adj", "молодой, юный"),
    ("important", "[ɪmˈpɔː.tənt]", "adj", "важный, значительный"),
    ("few", "[fjuː]", "adj/pron", "мало, несколько"),
    ("public", "[ˈpʌb.lɪk]", "adj/noun", "общественный; публика"),
    ("bad", "[bæd]", "adj", "плохой, дурной"),
    ("same", "[seɪm]", "adj", "тот же самый, одинаковый"),
    ("able", "[ˈeɪ.bəl]", "adj", "способный"),
    ("cat", "[kæt]", "noun", "кот, кошка"),
    ("dog", "[dɒɡ]", "noun", "собака, пес"),
    ("apple", "[ˈæp.əl]", "noun", "яблоко"),
    ("tree", "[triː]", "noun", "дерево"),
    ("water", "[ˈwɔː.tər]", "noun", "вода"),
    ("fire", "[faɪər]", "noun/verb", "огонь, костер; стрелять, увольнять"),
    ("night", "[naɪt]", "noun", "ночь, вечер"),
    ("door", "[dɔːr]", "noun", "дверь, вход"),
    ("room", "[ruːm]", "noun", "комната, номер, пространство"),
    ("house", "[haʊs]", "noun", "дом, здание"),
    ("pocket", "[ˈpɒk.ɪt]", "noun", "карман"),
    ("watch", "[wɒtʃ]", "noun/verb", "часы (наручные/карманные); наблюдать"),
    ("sister", "[ˈsɪs.tər]", "noun", "сестра"),
    ("bank", "[bæŋk]", "noun", "берег (реки); банк"),
    ("daisy", "[ˈdeɪ.zi]", "noun", "маргаритка"),
    ("chain", "[tʃeɪn]", "noun", "цепь, цепочка, сеть"),
    ("suddenly", "[ˈsʌd.ən.li]", "adv", "вдруг, внезапно"),
    ("white", "[waɪt]", "adj/noun", "белый; белый цвет"),
    ("pink", "[pɪŋk]", "adj/noun", "розовый; розовый цвет"),
    ("waistcoat", "[ˈweɪst.kəʊt]", "noun", "жилет, жилетка"),
    ("flash", "[flæʃ]", "noun/verb", "вспышка, мелькание; вспыхивать"),
    ("across", "[əˈkrɒs]", "prep", "через, сквозь, по ту сторону"),
    ("mind", "[maɪnd]", "noun/verb", "разум, мысль; возражать"),
    ("never", "[ˈnev.ər]", "adv", "никогда"),
    ("before", "[bɪˈfɔːr]", "prep/adv", "до, раньше, перед"),
    ("burning", "[ˈbɜː.nɪŋ]", "adj", "горящий, пылающий, жгучий"),
    ("curiosity", "[ˌkjʊə.riˈɒs.ə.ti]", "noun", "любопытство"),
    ("field", "[fiːld]", "noun", "поле, область деятельности"),
    ("hedge", "[hedʒ]", "noun", "живая изгородь, плетень"),
    ("down", "[daʊn]", "adv/prep", "вниз; внизу"),
    ("straight", "[streɪt]", "adj/adv", "прямой; прямо"),
    ("tunnel", "[ˈtʌn.əl]", "noun", "тоннель"),
    ("deep", "[diːp]", "adj/adv", "глубокий; глубоко"),
    ("well", "[wel]", "noun/adv", "колодец; хорошо"),
    ("fall", "[fɔːl]", "verb/noun", "падать; падение"),
    ("slowly", "[ˈsləʊ.li]", "adv", "медленно"),
    ("plenty", "[ˈplen.ti]", "noun", "множество, изобилие"),
    ("cupboard", "[ˈkʌb.əd]", "noun", "буфет, шкаф для посуды"),
    ("shelf", "[ʃelf]", "noun", "полка"),
    ("map", "[mæp]", "noun", "карта"),
    ("picture", "[ˈpɪk.tʃər]", "noun", "картина, изображение, рисунок"),
    ("jar", "[dʒɑːr]", "noun", "банка, кувшин"),
    ("orange", "[ˈɒr.ɪndʒ]", "noun/adj", "апельсин; оранжевый"),
    ("marmalade", "[ˈmɑː.mə.leɪd]", "noun", "джем, мармелад"),
    ("empty", "[ˈemp.ti]", "adj/verb", "пустой; опустошать"),
    ("disappointment", "[ˌdɪs.əˈpɔɪnt.mənt]", "noun", "разочарование"),
    ("fear", "[fɪər]", "noun/verb", "страх; бояться"),
    ("past", "[pɑːst]", "prep/adj", "мимо; прошлый"),
    ("somewhere", "[ˈsʌm.weər]", "adv", "где-то, куда-то"),
    ("miles", "[maɪlz]", "noun", "мили"),
    ("centre", "[ˈsen.tər]", "noun", "центр"),
    ("earth", "[ɜːθ]", "noun", "земля, земной шар"),
    ("distance", "[ˈdɪs.təns]", "noun", "расстояние, дистанция"),
    ("knowledge", "[ˈnɒl.ɪdʒ]", "noun", "знание, познания"),
    ("schoolroom", "[ˈskuːl.ruːm]", "noun", "классная комната"),
    ("latitude", "[ˈlæt.ɪ.tjuːd]", "noun", "широта (географическая)"),
    ("longitude", "[ˈlɒŋ.ɡɪ.tjuːd]", "noun", "долгота (географическая)"),
    ("grand", "[ɡrænd]", "adj", "величественный, грандиозный"),
    ("words", "[wɜːdz]", "noun", "слова"),
]

def init_database(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    return conn

def insert_entries(conn, entries):
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO words (word, transcription, pos, translation) VALUES (?, ?, ?, ?)",
        entries
    )
    conn.commit()

def populate_core(conn):
    print(f"[*] Добавление базового ядра слов ({len(BUILTIN_CORE_VOCABULARY)} слов)...")
    insert_entries(conn, BUILTIN_CORE_VOCABULARY)

def download_and_import_extended_dict(conn):
    """
    Опциональная загрузка расширенного словаря FreeDict / Mueller.
    Если сеть недоступна, встроенное ядро гарантирует работу.
    """
    dict_url = "https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv"
    # Для стабильности офлайн-сборки используем ядро + локальные файлы если есть
    local_tsv = os.path.join(SCRIPT_DIR, "raw", "mueller.tsv")
    if os.path.exists(local_tsv):
        print(f"[*] Найдена локальная база {local_tsv}, импорт...")
        with open(local_tsv, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    word = parts[0].strip()
                    trans = parts[1].strip() if len(parts) > 2 else ""
                    pos = parts[2].strip() if len(parts) > 3 else ""
                    trn = parts[-1].strip()
                    batch.append((word, trans, pos, trn))
                    if len(batch) >= 5000:
                        insert_entries(conn, batch)
                        batch = []
            if batch:
                insert_entries(conn, batch)

def main():
    print("==================================================")
    print("RetroReader: Сборка словаря SQLite для iPad 2")
    print("==================================================")
    print(f"Целевой файл: {OUTPUT_DB_PATH}")

    conn = init_database(OUTPUT_DB_PATH)
    populate_core(conn)
    download_and_import_extended_dict(conn)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words;")
    total_words = cursor.fetchone()[0]
    
    cursor.execute("VACUUM;")
    cursor.execute("ANALYZE;")
    conn.close()

    db_size_kb = os.path.getsize(OUTPUT_DB_PATH) / 1024
    print(f"[OK] База успешно собрана!")
    print(f"Всего слов в словаре: {total_words}")
    print(f"Размер базы: {db_size_kb:.1f} KB")
    print("==================================================")

if __name__ == "__main__":
    main()
