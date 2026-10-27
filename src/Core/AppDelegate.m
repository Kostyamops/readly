#import "AppDelegate.h"
#import <sys/utsname.h>

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
    self.window.backgroundColor = [UIColor whiteColor];

    // Smoke Test экран для подтверждения успешного запуска
    UIViewController *rootVC = [[UIViewController alloc] init];
    rootVC.view.backgroundColor = [UIColor colorWithRed:0.96 green:0.96 blue:0.94 alpha:1.0];

    UILabel *lblTitle = [[UILabel alloc] initWithFrame:CGRectMake(40, 200, rootVC.view.bounds.size.width - 80, 50)];
    lblTitle.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    lblTitle.font = [UIFont boldSystemFontOfSize:28.0];
    lblTitle.textAlignment = NSTextAlignmentCenter;
    lblTitle.textColor = [UIColor colorWithRed:0.1 green:0.1 blue:0.12 alpha:1.0];
    lblTitle.text = @"RetroReader Smoke Test";
    [rootVC.view addSubview:lblTitle];

    // Вывод системной информации iPad
    struct utsname systemInfo;
    uname(&systemInfo);
    NSString *deviceModel = [NSString stringWithCString:systemInfo.machine encoding:NSUTF8StringEncoding];

    UILabel *lblInfo = [[UILabel alloc] initWithFrame:CGRectMake(40, 270, rootVC.view.bounds.size.width - 80, 40)];
    lblInfo.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    lblInfo.font = [UIFont systemFontOfSize:18.0];
    lblInfo.textAlignment = NSTextAlignmentCenter;
    lblInfo.textColor = [UIColor colorWithWhite:0.4 alpha:1.0];
    lblInfo.text = [NSString stringWithFormat:@"Device: %@ | iOS: %@", deviceModel, [[UIDevice currentDevice] systemVersion]];
    [rootVC.view addSubview:lblInfo];

    self.window.rootViewController = rootVC;
    [self.window makeKeyAndVisible];

    NSLog(@"[RetroReader] Smoke Test запущен успешно на устройстве %@ (iOS %@)", deviceModel, [[UIDevice currentDevice] systemVersion]);
    return YES;
}

@end
