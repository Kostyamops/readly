#import "RRTranslationViewController.h"

@interface RRTranslationViewController ()
@property (nonatomic, strong) UILabel *lblWord;
@property (nonatomic, strong) UILabel *lblTranscription;
@property (nonatomic, strong) UILabel *lblPos;
@property (nonatomic, strong) UITextView *txtTranslation;
@end

@implementation RRTranslationViewController

- (instancetype)initWithWordEntry:(RRWordEntry *)wordEntry {
    self = [super initWithNibName:nil bundle:nil];
    if (self) {
        _wordEntry = wordEntry;
        // Размер всплывающего окна (бабла) на экране iPad
        self.preferredContentSize = CGSizeMake(300.0, 160.0);
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor colorWithWhite:0.98 alpha:1.0];
    
    // 1. Слово
    self.lblWord = [[UILabel alloc] initWithFrame:CGRectMake(16, 12, 190, 24)];
    self.lblWord.font = [UIFont boldSystemFontOfSize:19.0];
    self.lblWord.textColor = [UIColor colorWithRed:0.1 green:0.1 blue:0.12 alpha:1.0];
    self.lblWord.text = self.wordEntry.word ?: @"";
    [self.view addSubview:self.lblWord];
    
    // 2. Бейдж части речи (pos)
    if (self.wordEntry.partOfSpeech.length > 0) {
        self.lblPos = [[UILabel alloc] initWithFrame:CGRectMake(210, 13, 75, 20)];
        self.lblPos.font = [UIFont systemFontOfSize:11.0];
        self.lblPos.textColor = [UIColor whiteColor];
        self.lblPos.backgroundColor = [UIColor colorWithRed:0.25 green:0.5 blue:0.8 alpha:0.9];
        self.lblPos.textAlignment = NSTextAlignmentCenter;
        self.lblPos.layer.cornerRadius = 4.0;
        self.lblPos.layer.masksToBounds = YES;
        self.lblPos.text = self.wordEntry.partOfSpeech;
        [self.view addSubview:self.lblPos];
    }
    
    // 3. Транскрипция
    self.lblTranscription = [[UILabel alloc] initWithFrame:CGRectMake(16, 38, 268, 18)];
    self.lblTranscription.font = [UIFont italicSystemFontOfSize:13.0];
    self.lblTranscription.textColor = [UIColor colorWithRed:0.4 green:0.4 blue:0.45 alpha:1.0];
    self.lblTranscription.text = self.wordEntry.transcription ?: @"";
    [self.view addSubview:self.lblTranscription];
    
    // Разделитель
    UIView *divider = [[UIView alloc] initWithFrame:CGRectMake(16, 60, 268, 1)];
    divider.backgroundColor = [UIColor colorWithWhite:0.88 alpha:1.0];
    [self.view addSubview:divider];
    
    // 4. Текст перевода
    self.txtTranslation = [[UITextView alloc] initWithFrame:CGRectMake(12, 64, 276, 88)];
    self.txtTranslation.font = [UIFont systemFontOfSize:15.0];
    self.txtTranslation.textColor = [UIColor colorWithRed:0.2 green:0.2 blue:0.2 alpha:1.0];
    self.txtTranslation.backgroundColor = [UIColor clearColor];
    self.txtTranslation.editable = NO;
    self.txtTranslation.selectable = NO;
    self.txtTranslation.text = self.wordEntry.translation ?: @"Перевод не найден";
    [self.view addSubview:self.txtTranslation];
}

@end
