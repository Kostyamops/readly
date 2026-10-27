#ifndef Constants_h
#define Constants_h

#import <Foundation/Foundation.h>

// Схема кастомного протокола для передачи событий из JS в Objective-C
#define kRRReaderBridgeScheme @"reader-bridge"
#define kRRReaderActionWordTap @"wordTap"

// Настройки верстки читалки (размеры экрана iPad 2)
#define kRRIpadScreenWidth  1024.0
#define kRRIpadScreenHeight 768.0

// Имена дефолтных ресурсов
#define kRRDefaultDictionaryName @"dictionary.sqlite"
#define kRRDefaultBookName       @"sample.epub"

#endif /* Constants_h */
