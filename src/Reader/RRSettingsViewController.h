#import <UIKit/UIKit.h>
#import "RRReaderSettings.h"

@protocol RRSettingsViewControllerDelegate <NSObject>
- (void)settingsViewControllerDidChangeSettings:(RRReaderSettings *)settings;
@end

@interface RRSettingsViewController : UIViewController

@property (nonatomic, weak) id<RRSettingsViewControllerDelegate> delegate;

@end
