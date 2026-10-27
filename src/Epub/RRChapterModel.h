#import <Foundation/Foundation.h>

@interface RRChapterModel : NSObject

@property (nonatomic, copy) NSString *chapterId;
@property (nonatomic, copy) NSString *title;
@property (nonatomic, copy) NSString *relativeHtmlPath; // Относительный путь от папки книги
@property (nonatomic, copy) NSString *absoluteHtmlPath; // Полный путь на диске iPad
@property (nonatomic, assign) NSInteger orderIndex;

@end
