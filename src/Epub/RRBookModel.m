#import "RRBookModel.h"

@implementation RRBookModel

- (NSString *)description {
    return [NSString stringWithFormat:@"<RRBookModel: '%@' by %@, %lu chapters>",
            self.title ?: @"Untitled", self.author ?: @"Unknown", (unsigned long)self.chapters.count];
}

@end
