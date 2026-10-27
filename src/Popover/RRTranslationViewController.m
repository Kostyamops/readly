#import "RRTranslationViewController.h"

@implementation RRTranslationViewController

- (instancetype)initWithWordEntry:(RRWordEntry *)wordEntry {
    self = [super initWithNibName:nil bundle:nil];
    if (self) {
        _wordEntry = wordEntry;
        self.preferredContentSize = CGSizeMake(300, 160);
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.preferredContentSize = CGSizeMake(300, 160);
    self.view.backgroundColor = [UIColor colorWithRed:0.98 green:0.98 blue:0.97 alpha:1.0];
    
    CGFloat contentWidth = 300.0;
    
    // 1. Заголовок слова (19pt bold)
    NSString *wordText = self.wordEntry ? self.wordEntry.word : @"";
    self.lblWord = [[UILabel alloc] initWithFrame:CGRectMake(16, 12, 180, 24)];
    self.lblWord.font = [UIFont boldSystemFontOfSize:19.0];
    self.lblWord.textColor = [UIColor colorWithRed:0.12 green:0.12 blue:0.14 alpha:1.0];
    self.lblWord.text = wordText;
    [self.view addSubview:self.lblWord];
    
    // Расчет ширины слова для правильного размещения бейджа части речи
    CGSize wordSize = [wordText sizeWithAttributes:@{NSFontAttributeName: self.lblWord.font}];
    CGFloat badgeX = 16 + wordSize.width + 8;
    if (badgeX > 220) badgeX = 220;
    
    // 2. Цветной бейдж части речи (скругление 4px, фоновый цвет)
    self.lblPos = [[UILabel alloc] initWithFrame:CGRectMake(badgeX, 14, 56, 18)];
    self.lblPos.font = [UIFont systemFontOfSize:11.0];
    self.lblPos.textColor = [UIColor colorWithRed:0.15 green:0.42 blue:0.65 alpha:1.0];
    self.lblPos.backgroundColor = [UIColor colorWithRed:0.88 green:0.93 blue:0.98 alpha:1.0];
    self.lblPos.layer.cornerRadius = 4.0;
    self.lblPos.layer.masksToBounds = YES;
    self.lblPos.textAlignment = NSTextAlignmentCenter;
    
    if (self.wordEntry.partOfSpeech && self.wordEntry.partOfSpeech.length > 0) {
        self.lblPos.text = self.wordEntry.partOfSpeech;
        [self.view addSubview:self.lblPos];
    }
    
    // 3. Транскрипция (13pt italic)
    self.lblTranscription = [[UILabel alloc] initWithFrame:CGRectMake(16, 38, contentWidth - 32, 18)];
    self.lblTranscription.font = [UIFont italicSystemFontOfSize:13.0];
    self.lblTranscription.textColor = [UIColor colorWithWhite:0.45 alpha:1.0];
    self.lblTranscription.text = self.wordEntry.transcription ?: @"";
    [self.view addSubview:self.lblTranscription];
    
    // 4. UITextView для текста перевода со скроллом (editable = NO, selectable = NO)
    self.txtTranslation = [[UITextView alloc] initWithFrame:CGRectMake(12, 60, contentWidth - 24, 90)];
    self.txtTranslation.font = [UIFont systemFontOfSize:14.0];
    self.txtTranslation.textColor = [UIColor colorWithRed:0.18 green:0.18 blue:0.20 alpha:1.0];
    self.txtTranslation.backgroundColor = [UIColor clearColor];
    self.txtTranslation.editable = NO;
    self.txtTranslation.selectable = NO;
    self.txtTranslation.showsVerticalScrollIndicator = YES;
    self.txtTranslation.text = self.wordEntry.translation ?: @"Перевод не найден";
    [self.view addSubview:self.txtTranslation];
}

@end
