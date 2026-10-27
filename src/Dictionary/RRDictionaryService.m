#import "RRDictionaryService.h"
#import <sqlite3.h>

@interface RRDictionaryService () {
    sqlite3 *_db;
    sqlite3_stmt *_lookupStmt;
}
@property (nonatomic, copy) NSString *dbPath;
@property (nonatomic, strong) NSLinguisticTagger *tagger;
@end

@implementation RRDictionaryService

+ (instancetype)sharedService {
    static RRDictionaryService *sharedInstance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        sharedInstance = [[RRDictionaryService alloc] init];
    });
    return sharedInstance;
}

- (instancetype)init {
    self = [super init];
    if (self) {
        _db = NULL;
        _lookupStmt = NULL;
        
        // Системный анализатор языка iOS 9 для лемматизации
        NSArray *schemes = @[NSLinguisticTagSchemeLemma];
        _tagger = [[NSLinguisticTagger alloc] initWithTagSchemes:schemes options:0];
    }
    return self;
}

- (void)dealloc {
    [self closeDatabase];
}

- (BOOL)openDatabaseWithPath:(NSString *)path error:(NSError **)error {
    if (_db != NULL) {
        if ([self.dbPath isEqualToString:path]) {
            return YES; // База уже открыта
        }
        [self closeDatabase];
    }
    
    self.dbPath = path;
    
    // Открываем базу только на чтение (SQLITE_OPEN_READONLY), что уменьшает расход RAM
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
    if (sqlite3_open_v2([path UTF8String], &_db, flags, NULL) != SQLITE_OK) {
        if (error) {
            NSString *msg = [NSString stringWithUTF8String:sqlite3_errmsg(_db)];
            *error = [NSError errorWithDomain:@"RRDictionaryError"
                                         code:101
                                     userInfo:@{NSLocalizedDescriptionKey: msg}];
        }
        [self closeDatabase];
        return NO;
    }
    
    // Предкомпиляция запроса один раз для максимальной производительности O(1)
    const char *query = "SELECT transcription, pos, translation FROM words WHERE word = ? LIMIT 1;";
    if (sqlite3_prepare_v2(_db, query, -1, &_lookupStmt, NULL) != SQLITE_OK) {
        if (error) {
            NSString *msg = [NSString stringWithUTF8String:sqlite3_errmsg(_db)];
            *error = [NSError errorWithDomain:@"RRDictionaryError"
                                         code:102
                                     userInfo:@{NSLocalizedDescriptionKey: msg}];
        }
        [self closeDatabase];
        return NO;
    }
    
    return YES;
}

- (void)closeDatabase {
    if (_lookupStmt) {
        sqlite3_finalize(_lookupStmt);
        _lookupStmt = NULL;
    }
    if (_db) {
        sqlite3_close(_db);
        _db = NULL;
    }
    self.dbPath = nil;
}

- (NSString *)cleanWord:(NSString *)rawWord {
    if (!rawWord || rawWord.length == 0) return nil;
    
    // Тримминг пробелов и краевых знаков пунктуации
    NSCharacterSet *punctAndWhitespace = [NSCharacterSet characterSetWithCharactersInString:@" \t\r\n.,!?;:\"'“”‘’()[]{}<>-—_`~*#&^%$@/\\"];
    NSString *cleaned = [rawWord stringByTrimmingCharactersInSet:punctAndWhitespace];
    return cleaned.length > 0 ? [cleaned lowercaseString] : nil;
}

- (NSString *)lemmatizeWord:(NSString *)rawWord {
    NSString *word = [self cleanWord:rawWord];
    if (!word || word.length == 0) return nil;
    
    [self.tagger setString:word];
    
    NSRange range = NSMakeRange(0, word.length);
    NSString *lemma = [self.tagger tagAtIndex:0
                                       scheme:NSLinguisticTagSchemeLemma
                                   tokenRange:NULL
                                sentenceRange:NULL];
    
    if (lemma && lemma.length > 0) {
        return [lemma lowercaseString];
    }
    
    return word;
}

- (RRWordEntry *)executeLookup:(NSString *)targetWord {
    if (!_lookupStmt || !targetWord || targetWord.length == 0) return nil;
    
    sqlite3_reset(_lookupStmt);
    sqlite3_clear_bindings(_lookupStmt);
    
    sqlite3_bind_text(_lookupStmt, 1, [targetWord UTF8String], -1, SQLITE_TRANSIENT);
    
    RRWordEntry *entry = nil;
    if (sqlite3_step(_lookupStmt) == SQLITE_ROW) {
        const char *trans = (const char *)sqlite3_column_text(_lookupStmt, 0);
        const char *pos   = (const char *)sqlite3_column_text(_lookupStmt, 1);
        const char *trn   = (const char *)sqlite3_column_text(_lookupStmt, 2);
        
        NSString *transcription = trans ? [NSString stringWithUTF8String:trans] : @"";
        NSString *partOfSpeech  = pos   ? [NSString stringWithUTF8String:pos]   : @"";
        NSString *translation   = trn   ? [NSString stringWithUTF8String:trn]   : @"";
        
        entry = [[RRWordEntry alloc] initWithWord:targetWord
                                    transcription:transcription
                                     partOfSpeech:partOfSpeech
                                      translation:translation];
    }
    
    sqlite3_reset(_lookupStmt);
    return entry;
}

- (RRWordEntry *)lookupWord:(NSString *)word {
    NSString *cleaned = [self cleanWord:word];
    if (!cleaned) return nil;
    
    // 1. Попытка прямого поиска
    RRWordEntry *entry = [self executeLookup:cleaned];
    if (entry) {
        return entry;
    }
    
    // 2. Попытка лемматизации (running -> run, books -> book, was -> be)
    NSString *lemma = [self lemmatizeWord:cleaned];
    if (lemma && ![lemma isEqualToString:cleaned]) {
        entry = [self executeLookup:lemma];
        if (entry) {
            return entry;
        }
    }
    
    return nil;
}

@end
