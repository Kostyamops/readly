#import "RREpubParser.h"
#import "RRZipExtractor.h"

#pragma mark - SAX парсер META-INF/container.xml

@interface RRContainerXMLParser : NSObject <NSXMLParserDelegate>
@property (nonatomic, copy) NSString *opfRelativePath;
@end

@implementation RRContainerXMLParser

- (void)parser:(NSXMLParser *)parser
didStartElement:(NSString *)elementName
  namespaceURI:(NSString *)namespaceURI
 qualifiedName:(NSString *)qName
    attributes:(NSDictionary<NSString *, NSString *> *)attributeDict {
    if ([elementName isEqualToString:@"rootfile"]) {
        NSString *mediaType = attributeDict[@"media-type"];
        if (!mediaType || [mediaType isEqualToString:@"application/oebps-package+xml"]) {
            self.opfRelativePath = attributeDict[@"full-path"];
        }
    }
}

@end

#pragma mark - SAX парсер content.opf

@interface RROpfXMLParser : NSObject <NSXMLParserDelegate>
@property (nonatomic, copy) NSString *title;
@property (nonatomic, copy) NSString *author;
@property (nonatomic, strong) NSMutableDictionary<NSString *, NSString *> *manifest; // id -> href
@property (nonatomic, strong) NSMutableArray<NSString *> *spine;                      // itemref idrefs
@property (nonatomic, copy) NSString *currentElement;
@property (nonatomic, strong) NSMutableString *currentString;
@end

@implementation RROpfXMLParser

- (instancetype)init {
    self = [super init];
    if (self) {
        _manifest = [NSMutableDictionary dictionary];
        _spine = [NSMutableArray array];
    }
    return self;
}

- (void)parser:(NSXMLParser *)parser
didStartElement:(NSString *)elementName
  namespaceURI:(NSString *)namespaceURI
 qualifiedName:(NSString *)qName
    attributes:(NSDictionary<NSString *, NSString *> *)attributeDict {
    self.currentElement = elementName;
    
    if ([elementName isEqualToString:@"item"]) {
        NSString *itemId = attributeDict[@"id"];
        NSString *href = attributeDict[@"href"];
        if (itemId && href) {
            self.manifest[itemId] = href;
        }
    } else if ([elementName isEqualToString:@"itemref"]) {
        NSString *idref = attributeDict[@"idref"];
        if (idref) {
            [self.spine addObject:idref];
        }
    } else if ([elementName isEqualToString:@"dc:title"] || [elementName isEqualToString:@"dc:creator"]) {
        self.currentString = [NSMutableString string];
    }
}

- (void)parser:(NSXMLParser *)parser foundCharacters:(NSString *)string {
    if (self.currentString) {
        [self.currentString appendString:string];
    }
}

- (void)parser:(NSXMLParser *)parser
 didEndElement:(NSString *)elementName
  namespaceURI:(NSString *)namespaceURI
 qualifiedName:(NSString *)qName {
    if ([elementName isEqualToString:@"dc:title"]) {
        self.title = [self.currentString stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        self.currentString = nil;
    } else if ([elementName isEqualToString:@"dc:creator"]) {
        self.author = [self.currentString stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        self.currentString = nil;
    }
    self.currentElement = nil;
}

@end

#pragma mark - RREpubParser

@implementation RREpubParser

+ (RRBookModel *)parseEpubAtPath:(NSString *)epubFilePath error:(NSError **)error {
    NSFileManager *fm = [NSFileManager defaultManager];
    if (![fm fileExistsAtPath:epubFilePath]) {
        if (error) {
            *error = [NSError errorWithDomain:@"RREpubParser"
                                         code:301
                                     userInfo:@{NSLocalizedDescriptionKey: @"Файл EPUB не найден"}];
        }
        return nil;
    }
    
    // 1. Получаем директорию кэша
    NSString *destDir = [RRZipExtractor cacheDirectoryForBookPath:epubFilePath];
    NSString *containerPath = [destDir stringByAppendingPathComponent:@"META-INF/container.xml"];
    
    // Распаковка при отсутствии в кэше
    if (![fm fileExistsAtPath:containerPath]) {
        BOOL ok = [RRZipExtractor unzipFileAtPath:epubFilePath toDestination:destDir error:error];
        if (!ok) {
            return nil;
        }
    }
    
    // 2. Парсим META-INF/container.xml
    NSData *containerData = [NSData dataWithContentsOfFile:containerPath];
    if (!containerData) {
        if (error) {
            *error = [NSError errorWithDomain:@"RREpubParser"
                                         code:302
                                     userInfo:@{NSLocalizedDescriptionKey: @"Не удалось прочитать container.xml"}];
        }
        return nil;
    }
    
    RRContainerXMLParser *containerParser = [[RRContainerXMLParser alloc] init];
    NSXMLParser *xmlParser1 = [[NSXMLParser alloc] initWithData:containerData];
    xmlParser1.delegate = containerParser;
    [xmlParser1 parse];
    
    if (!containerParser.opfRelativePath) {
        if (error) {
            *error = [NSError errorWithDomain:@"RREpubParser"
                                         code:303
                                     userInfo:@{NSLocalizedDescriptionKey: @"В container.xml отсутствует rootfile"}];
        }
        return nil;
    }
    
    // 3. Парсим content.opf
    NSString *opfFullPath = [destDir stringByAppendingPathComponent:containerParser.opfRelativePath];
    NSData *opfData = [NSData dataWithContentsOfFile:opfFullPath];
    if (!opfData) {
        if (error) {
            *error = [NSError errorWithDomain:@"RREpubParser"
                                         code:304
                                     userInfo:@{NSLocalizedDescriptionKey: @"Не удалось прочитать OPF файл"}];
        }
        return nil;
    }
    
    RROpfXMLParser *opfParser = [[RROpfXMLParser alloc] init];
    NSXMLParser *xmlParser2 = [[NSXMLParser alloc] initWithData:opfData];
    xmlParser2.delegate = opfParser;
    [xmlParser2 parse];
    
    NSString *opfFolder = [opfFullPath stringByDeletingLastPathComponent];
    
    // 4. Формируем список глав в порядке чтения spine
    NSMutableArray<RRChapterModel *> *chapters = [NSMutableArray array];
    NSInteger index = 0;
    
    for (NSString *spineId in opfParser.spine) {
        NSString *href = opfParser.manifest[spineId];
        if (href) {
            RRChapterModel *chapter = [[RRChapterModel alloc] init];
            chapter.chapterId = spineId;
            chapter.title = [NSString stringWithFormat:@"Chapter %ld", (long)(index + 1)];
            chapter.relativeHtmlPath = href;
            chapter.absoluteHtmlPath = [opfFolder stringByAppendingPathComponent:href];
            chapter.orderIndex = index;
            [chapters addObject:chapter];
            index++;
        }
    }
    
    RRBookModel *book = [[RRBookModel alloc] init];
    book.title = opfParser.title ?: @"Untitled Book";
    book.author = opfParser.author ?: @"Unknown Author";
    book.epubFilePath = epubFilePath;
    book.baseFolderPath = destDir;
    book.opfFolderPath = opfFolder;
    book.chapters = chapters;
    
    // Поиск обложки книги в manifest
    for (NSString *key in opfParser.manifest) {
        NSString *val = opfParser.manifest[key];
        NSString *lowerKey = [key lowercaseString];
        NSString *lowerVal = [val lowercaseString];
        if ([lowerKey rangeOfString:@"cover"].location != NSNotFound ||
            [lowerVal rangeOfString:@"cover"].location != NSNotFound) {
            if ([lowerVal hasSuffix:@".jpg"] || [lowerVal hasSuffix:@".jpeg"] || [lowerVal hasSuffix:@".png"]) {
                book.coverImagePath = [opfFolder stringByAppendingPathComponent:val];
                break;
            }
        }
    }
    
    return book;
}

@end
