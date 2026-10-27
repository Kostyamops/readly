#import <Foundation/Foundation.h>

@interface RRChapterModel : NSObject

@property (nonatomic, copy) NSString *chapterId;
@property (nonatomic, copy) NSString *title;
@property (nonatomic, copy) NSString *relativeHtmlPath;
@property (nonatomic, copy) NSString *absoluteHtmlPath;
@property (nonatomic, assign) NSInteger orderIndex;

@end
