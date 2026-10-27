#import <UIKit/UIKit.h>
#import "RRWordEntry.h"

@interface RRTranslationViewController : UIViewController

@property (nonatomic, strong) RRWordEntry *wordEntry;
@property (nonatomic, strong) UILabel *lblWord;
@property (nonatomic, strong) UILabel *lblTranscription;
@property (nonatomic, strong) UILabel *lblPos;
@property (nonatomic, strong) UITextView *txtTranslation;

- (instancetype)initWithWordEntry:(RRWordEntry *)wordEntry;

@end
