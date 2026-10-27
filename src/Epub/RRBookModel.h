#import <Foundation/Foundation.h>
#import "RRChapterModel.h"

@interface RRBookModel : NSObject

@property (nonatomic, copy) NSString *title;
@property (nonatomic, copy) NSString *author;
@property (nonatomic, copy) NSString *baseFolderPath;
@property (nonatomic, copy) NSString *opfFolderPath; // Папка где лежит content.opf (например OEBPS)
@property (nonatomic, strong) NSArray<RRChapterModel *> *chapters;

@end
