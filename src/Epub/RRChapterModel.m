#import "RRChapterModel.h"

@implementation RRChapterModel

- (NSString *)description {
    return [NSString stringWithFormat:@"<RRChapterModel #%ld: '%@' -> %@>",
            (long)self.orderIndex, self.title ?: self.chapterId, self.relativeHtmlPath];
}

@end
