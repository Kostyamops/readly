TARGET := iphone:clang:latest:9.3
ARCHS := armv7

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = RetroReader

RetroReader_FILES = \
    src/main.m \
    src/Core/AppDelegate.m \
    src/Dictionary/RRWordEntry.m \
    src/Dictionary/RRDictionaryService.m

RetroReader_FRAMEWORKS = UIKit Foundation CoreGraphics
RetroReader_LIBRARIES = sqlite3 z
RetroReader_CFLAGS = -fobjc-arc -Isrc/Core -Isrc/Dictionary

RetroReader_RESOURCE_DIRS = resources

include $(THEOS_MAKE_PATH)/application.mk
