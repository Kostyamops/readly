#import "RRReaderSettings.h"

static NSString * const kPrefFontSize = @"RRPrefFontSize";
static NSString * const kPrefFontFamily = @"RRPrefFontFamily";
static NSString * const kPrefTheme = @"RRPrefTheme";

@implementation RRReaderSettings

+ (instancetype)sharedSettings {
    static RRReaderSettings *instance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        instance = [[RRReaderSettings alloc] init];
        [instance load];
    });
    return instance;
}

- (void)load {
    NSUserDefaults *defs = [NSUserDefaults standardUserDefaults];
    
    NSInteger size = [defs integerForKey:kPrefFontSize];
    self.fontSize = (size >= 12 && size <= 36) ? size : 18;
    
    NSString *font = [defs stringForKey:kPrefFontFamily];
    self.fontFamily = (font && font.length > 0) ? font : @"Georgia";
    
    self.theme = (RRReaderTheme)[defs integerForKey:kPrefTheme];
    if (self.theme < 0 || self.theme > 2) {
        self.theme = RRReaderThemeSepia;
    }
}

- (void)save {
    NSUserDefaults *defs = [NSUserDefaults standardUserDefaults];
    [defs setInteger:self.fontSize forKey:kPrefFontSize];
    [defs setObject:self.fontFamily forKey:kPrefFontFamily];
    [defs setInteger:self.theme forKey:kPrefTheme];
    [defs synchronize];
}

- (NSString *)themeName {
    switch (self.theme) {
        case RRReaderThemeLight: return @"light";
        case RRReaderThemeNight: return @"night";
        case RRReaderThemeSepia:
        default: return @"sepia";
    }
}

- (UIColor *)backgroundColorForTheme {
    switch (self.theme) {
        case RRReaderThemeLight:
            return [UIColor colorWithRed:0.99 green:0.98 blue:0.96 alpha:1.0];
        case RRReaderThemeNight:
            return [UIColor colorWithRed:0.12 green:0.12 blue:0.12 alpha:1.0];
        case RRReaderThemeSepia:
        default:
            return [UIColor colorWithRed:0.96 green:0.93 blue:0.85 alpha:1.0];
    }
}

- (UIColor *)textColorForTheme {
    switch (self.theme) {
        case RRReaderThemeLight:
            return [UIColor colorWithRed:0.10 green:0.10 blue:0.10 alpha:1.0];
        case RRReaderThemeNight:
            return [UIColor colorWithRed:0.75 green:0.75 blue:0.75 alpha:1.0];
        case RRReaderThemeSepia:
        default:
            return [UIColor colorWithRed:0.24 green:0.17 blue:0.11 alpha:1.0];
    }
}

@end
