#import <UIKit/UIKit.h>

@interface RRBookShelfViewController : UIViewController <UITableViewDataSource, UITableViewDelegate>

@property (nonatomic, strong) UITableView *tableView;
@property (nonatomic, strong) NSMutableArray *books;

- (void)reloadBooks;

@end
