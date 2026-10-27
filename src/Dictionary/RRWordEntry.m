#import "RRWordEntry.h"

@implementation RRWordEntry

- (instancetype)initWithWord:(NSString *)word
               transcription:(NSString *)transcription
                partOfSpeech:(NSString *)partOfSpeech
                 translation:(NSString *)translation {
    self = [super init];
    if (self) {
        _word = [word copy];
        _transcription = [transcription copy];
        _partOfSpeech = [partOfSpeech copy];
        _translation = [translation copy];
    }
    return self;
}

- (NSString *)description {
    return [NSString stringWithFormat:@"<RRWordEntry: '%@' %@ [%@] -> %@>",
            self.word, self.transcription ?: @"", self.partOfSpeech ?: @"", self.translation];
}

@end
