#import "RRSettingsViewController.h"

@interface RRSettingsViewController ()

@property (nonatomic, strong) UILabel *lblFontSize;
@property (nonatomic, strong) UISegmentedControl *segFontFamily;
@property (nonatomic, strong) UISegmentedControl *segTheme;

@end

@implementation RRSettingsViewController

- (instancetype)init {
    self = [super initWithNibName:nil bundle:nil];
    if (self) {
        self.preferredContentSize = CGSizeMake(300, 210);
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor colorWithRed:0.98 green:0.98 blue:0.97 alpha:1.0];
    RRReaderSettings *settings = [RRReaderSettings sharedSettings];
    
    // 1. Заголовок
    UILabel *lblTitle = [[UILabel alloc] initWithFrame:CGRectMake(16, 12, 268, 22)];
    lblTitle.text = @"Настройки чтения";
    lblTitle.font = [UIFont boldSystemFontOfSize:16.0];
    lblTitle.textColor = [UIColor colorWithWhite:0.2 alpha:1.0];
    lblTitle.textAlignment = NSTextAlignmentCenter;
    [self.view addSubview:lblTitle];
    
    // 2. Блок размера шрифта: [ A- ]  18 pt  [ A+ ]
    UIButton *btnDec = [UIButton buttonWithType:UIButtonTypeSystem];
    btnDec.frame = CGRectMake(20, 44, 60, 36);
    [btnDec setTitle:@"A−" forState:UIControlStateNormal];
    btnDec.titleLabel.font = [UIFont systemFontOfSize:18.0 weight:UIFontWeightMedium];
    btnDec.backgroundColor = [UIColor colorWithWhite:0.92 alpha:1.0];
    btnDec.layer.cornerRadius = 6.0;
    [btnDec addTarget:self action:@selector(decreaseFontSize) forControlEvents:UIControlEventTouchUpInside];
    [self.view addSubview:btnDec];
    
    self.lblFontSize = [[UILabel alloc] initWithFrame:CGRectMake(90, 44, 120, 36)];
    self.lblFontSize.text = [NSString stringWithFormat:@"%ld pt", (long)settings.fontSize];
    self.lblFontSize.font = [UIFont systemFontOfSize:16.0 weight:UIFontWeightMedium];
    self.lblFontSize.textColor = [UIColor colorWithWhite:0.2 alpha:1.0];
    self.lblFontSize.textAlignment = NSTextAlignmentCenter;
    [self.view addSubview:self.lblFontSize];
    
    UIButton *btnInc = [UIButton buttonWithType:UIButtonTypeSystem];
    btnInc.frame = CGRectMake(220, 44, 60, 36);
    [btnInc setTitle:@"A+" forState:UIControlStateNormal];
    btnInc.titleLabel.font = [UIFont systemFontOfSize:20.0 weight:UIFontWeightMedium];
    btnInc.backgroundColor = [UIColor colorWithWhite:0.92 alpha:1.0];
    btnInc.layer.cornerRadius = 6.0;
    [btnInc addTarget:self action:@selector(increaseFontSize) forControlEvents:UIControlEventTouchUpInside];
    [self.view addSubview:btnInc];
    
    // 3. Выбор гарнитуры шрифта
    NSArray *fonts = @[@"Georgia", @"Palatino", @"Helvetica"];
    self.segFontFamily = [[UISegmentedControl alloc] initWithItems:fonts];
    self.segFontFamily.frame = CGRectMake(20, 96, 260, 34);
    
    NSInteger fontIdx = 0;
    if ([settings.fontFamily isEqualToString:@"Palatino"]) fontIdx = 1;
    else if ([settings.fontFamily isEqualToString:@"Helvetica"]) fontIdx = 2;
    self.segFontFamily.selectedSegmentIndex = fontIdx;
    [self.segFontFamily addTarget:self action:@selector(fontFamilyChanged:) forControlEvents:UIControlEventValueChanged];
    [self.view addSubview:self.segFontFamily];
    
    // 4. Выбор темы
    NSArray *themes = @[@"Светлая", @"Сепия", @"Ночь"];
    self.segTheme = [[UISegmentedControl alloc] initWithItems:themes];
    self.segTheme.frame = CGRectMake(20, 146, 260, 34);
    self.segTheme.selectedSegmentIndex = settings.theme;
    [self.segTheme addTarget:self action:@selector(themeChanged:) forControlEvents:UIControlEventValueChanged];
    [self.view addSubview:self.segTheme];
}

- (void)decreaseFontSize {
    RRReaderSettings *settings = [RRReaderSettings sharedSettings];
    if (settings.fontSize > 12) {
        settings.fontSize -= 2;
        [settings save];
        self.lblFontSize.text = [NSString stringWithFormat:@"%ld pt", (long)settings.fontSize];
        [self notifyChanged];
    }
}

- (void)increaseFontSize {
    RRReaderSettings *settings = [RRReaderSettings sharedSettings];
    if (settings.fontSize < 36) {
        settings.fontSize += 2;
        [settings save];
        self.lblFontSize.text = [NSString stringWithFormat:@"%ld pt", (long)settings.fontSize];
        [self notifyChanged];
    }
}

- (void)fontFamilyChanged:(UISegmentedControl *)seg {
    NSArray *fonts = @[@"Georgia", @"Palatino", @"Helvetica"];
    RRReaderSettings *settings = [RRReaderSettings sharedSettings];
    settings.fontFamily = fonts[seg.selectedSegmentIndex];
    [settings save];
    [self notifyChanged];
}

- (void)themeChanged:(UISegmentedControl *)seg {
    RRReaderSettings *settings = [RRReaderSettings sharedSettings];
    settings.theme = (RRReaderTheme)seg.selectedSegmentIndex;
    [settings save];
    [self notifyChanged];
}

- (void)notifyChanged {
    if ([self.delegate respondsToSelector:@selector(settingsViewControllerDidChangeSettings:)]) {
        [self.delegate settingsViewControllerDidChangeSettings:[RRReaderSettings sharedSettings]];
    }
}

@end
