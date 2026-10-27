export TARGET = iphone:clang:latest:9.3
export ARCHS = armv7

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = RetroReader

RetroReader_FILES = \
    src/main.m \
    src/Core/AppDelegate.m \
    src/Dictionary/RRWordEntry.m \
    src/Dictionary/RRDictionaryService.m \
    src/Epub/RRZipExtractor.m \
    src/Epub/RRChapterModel.m \
    src/Epub/RRBookModel.m \
    src/Epub/RREpubParser.m \
    src/Popover/RRTranslationViewController.m \
    src/Reader/RRReaderViewController.m

RetroReader_FRAMEWORKS = UIKit Foundation CoreGraphics
RetroReader_LIBRARIES = sqlite3 z
RetroReader_CFLAGS = -fobjc-arc -Isrc/Core -Isrc/Dictionary -Isrc/Epub -Isrc/Popover -Isrc/Reader

RetroReader_RESOURCE_DIRS = resources
RetroReader_RESOURCES = src/Reader/Assets/reader_style.css src/Reader/Assets/reader_bridge.js

include $(THEOS_MAKE_PATH)/application.mk
