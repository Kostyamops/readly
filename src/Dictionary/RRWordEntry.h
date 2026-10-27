#import <Foundation/Foundation.h>

@interface RRWordEntry : NSObject

@property (nonatomic, copy) NSString *word;
@property (nonatomic, copy) NSString *transcription;
@property (nonatomic, copy) NSString *partOfSpeech;
@property (nonatomic, copy) NSString *translation;

- (instancetype)initWithWord:(NSString *)word
               transcription:(NSString *)transcription
                partOfSpeech:(NSString *)partOfSpeech
                 translation:(NSString *)translation;

@end
