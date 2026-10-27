#!/usr/bin/env python3
"""
Скрипт сборки компактной офлайн-базы словаря SQLite для RetroReader (iOS 9.3.5 / iPad 2).
Реализует задачи: [M2-TASK-2.1.1.1 - M2-TASK-2.1.2.4]
"""

import os
import sys
import sqlite3

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

CORE_VOCABULARY = [
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
    ("pass", "[pɑːs]", "verb", "проходить, передавать, сдавать"),
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
    ("knife", "[naɪf]", "noun", "нож"),
]

def build_database():
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    if os.path.exists(OUTPUT_DB_PATH):
        os.remove(OUTPUT_DB_PATH)

    conn = sqlite3.connect(OUTPUT_DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)

    cursor.executemany(
        "INSERT OR IGNORE INTO words (word, transcription, pos, translation) VALUES (?, ?, ?, ?)",
        CORE_VOCABULARY
    )
    conn.commit()

    cursor.execute("VACUUM;")
    cursor.execute("ANALYZE;")
    conn.close()

    size_kb = os.path.getsize(OUTPUT_DB_PATH) / 1024
    print(f"[OK] База собрана: {OUTPUT_DB_PATH} ({size_kb:.1f} KB, {len(CORE_VOCABULARY)} слов)")

if __name__ == "__main__":
    build_database()
