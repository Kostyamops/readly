#import <UIKit/UIKit.h>
#import "RRWordEntry.h"

@interface RRTranslationViewController : UIViewController

@property (nonatomic, strong) RRWordEntry *wordEntry;

/**
 * Инициализация карточки с готовой словарной статьей
 */
- (instancetype)initWithWordEntry:(RRWordEntry *)wordEntry;

@end
