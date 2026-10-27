#import <UIKit/UIKit.h>
#import "RRBookModel.h"
#import "RRReaderSettings.h"
#import "RRSettingsViewController.h"

@interface RRReaderViewController : UIViewController <UIWebViewDelegate, UIPopoverPresentationControllerDelegate, UIGestureRecognizerDelegate, RRSettingsViewControllerDelegate>

@property (nonatomic, strong) RRBookModel *book;
@property (nonatomic, assign) NSInteger currentChapterIndex;
@property (nonatomic, assign) NSInteger currentPageIndex;
@property (nonatomic, assign) NSInteger totalPagesInChapter;

- (instancetype)initWithBook:(RRBookModel *)book;

- (void)loadChapterAtIndex:(NSInteger)chapterIndex;
- (void)nextPage;
- (void)prevPage;
- (void)handleWordTapURL:(NSURL *)url;

@end
