#import <UIKit/UIKit.h>
#import "RRBookModel.h"

@interface RRReaderViewController : UIViewController <UIWebViewDelegate, UIPopoverPresentationControllerDelegate>

@property (nonatomic, strong) RRBookModel *book;
@property (nonatomic, assign) NSInteger currentChapterIndex;
@property (nonatomic, assign) NSInteger currentPageIndex;
@property (nonatomic, assign) NSInteger totalPagesInChapter;

- (instancetype)initWithBook:(RRBookModel *)book;

- (void)loadChapterAtIndex:(NSInteger)chapterIndex;
- (void)nextPage;
- (void)prevPage;

@end
