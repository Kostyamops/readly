#import <UIKit/UIKit.h>

typedef NS_ENUM(NSInteger, RRReaderTheme) {
    RRReaderThemeLight = 0,
    RRReaderThemeSepia = 1,
    RRReaderThemeNight = 2
};

@interface RRReaderSettings : NSObject

@property (nonatomic, assign) NSInteger fontSize;
@property (nonatomic, copy) NSString *fontFamily;
@property (nonatomic, assign) RRReaderTheme theme;

+ (instancetype)sharedSettings;
- (void)save;

- (NSString *)themeName;
- (UIColor *)backgroundColorForTheme;
- (UIColor *)textColorForTheme;

@end
