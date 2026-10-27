#import "RRZipExtractor.h"
#import <zlib.h>
#import <CommonCrypto/CommonDigest.h>

#pragma pack(push, 1)
typedef struct {
    uint32_t signature; // 0x06054b50
    uint16_t diskNumber;
    uint16_t startDisk;
    uint16_t totalEntriesOnDisk;
    uint16_t totalEntries;
    uint32_t centralDirSize;
    uint32_t centralDirOffset;
    uint16_t commentLength;
} ZipEndOfCentralDir;

typedef struct {
    uint32_t signature; // 0x02014b50
    uint16_t versionMadeBy;
    uint16_t versionNeeded;
    uint16_t flags;
    uint16_t compressionMethod;
    uint16_t modTime;
    uint16_t modDate;
    uint32_t crc32;
    uint32_t compressedSize;
    uint32_t uncompressedSize;
    uint16_t filenameLength;
    uint16_t extraFieldLength;
    uint16_t commentLength;
    uint16_t diskNumberStart;
    uint16_t internalAttrs;
    uint32_t externalAttrs;
    uint32_t localHeaderOffset;
} ZipCentralDirHeader;

typedef struct {
    uint32_t signature; // 0x04034b50
    uint16_t versionNeeded;
    uint16_t flags;
    uint16_t compressionMethod;
    uint16_t modTime;
    uint16_t modDate;
    uint32_t crc32;
    uint32_t compressedSize;
    uint32_t uncompressedSize;
    uint16_t filenameLength;
    uint16_t extraFieldLength;
} ZipLocalHeader;
#pragma pack(pop)

@implementation RRZipExtractor

+ (NSString *)cacheDirectoryForBookPath:(NSString *)filePath {
    const char *str = [filePath UTF8String];
    unsigned char result[CC_MD5_DIGEST_LENGTH];
    CC_MD5(str, (CC_LONG)strlen(str), result);
    
    NSMutableString *hash = [NSMutableString stringWithCapacity:CC_MD5_DIGEST_LENGTH * 2];
    for (int i = 0; i < CC_MD5_DIGEST_LENGTH; i++) {
        [hash appendFormat:@"%02x", result[i]];
    }
    
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
    NSString *baseCache = [paths firstObject];
    return [baseCache stringByAppendingPathComponent:[NSString stringWithFormat:@"Books/%@", hash]];
}

+ (BOOL)unzipFileAtPath:(NSString *)filePath
          toDestination:(NSString *)destinationPath
                  error:(NSError **)error {
    NSFileManager *fm = [NSFileManager defaultManager];
    
    FILE *fp = fopen([filePath UTF8String], "rb");
    if (!fp) {
        if (error) {
            *error = [NSError errorWithDomain:@"RRZipError"
                                         code:201
                                     userInfo:@{NSLocalizedDescriptionKey: @"Не удалось открыть zip файл"}];
        }
        return NO;
    }
    
    // 1. Поиск конца Центральной Директории (EOCD) с конца файла
    fseek(fp, 0, SEEK_END);
    long fileSize = ftell(fp);
    if (fileSize < sizeof(ZipEndOfCentralDir)) {
        fclose(fp);
        return NO;
    }
    
    long searchLimit = fileSize > 65536 ? 65536 : fileSize;
    long searchStart = fileSize - searchLimit;
    fseek(fp, searchStart, SEEK_SET);
    
    uint8_t *searchBuffer = malloc(searchLimit);
    fread(searchBuffer, 1, searchLimit, fp);
    
    long eocdOffset = -1;
    for (long i = searchLimit - sizeof(ZipEndOfCentralDir); i >= 0; i--) {
        if (*(uint32_t *)(searchBuffer + i) == 0x06054b50) {
            eocdOffset = searchStart + i;
            break;
        }
    }
    free(searchBuffer);
    
    if (eocdOffset == -1) {
        fclose(fp);
        if (error) {
            *error = [NSError errorWithDomain:@"RRZipError"
                                         code:202
                                     userInfo:@{NSLocalizedDescriptionKey: @"Не найдена центральная директория ZIP"}];
        }
        return NO;
    }
    
    fseek(fp, eocdOffset, SEEK_SET);
    ZipEndOfCentralDir eocd;
    fread(&eocd, sizeof(ZipEndOfCentralDir), 1, fp);
    
    // 2. Чтение Центральной Директории
    fseek(fp, eocd.centralDirOffset, SEEK_SET);
    
    for (uint16_t entry = 0; entry < eocd.totalEntries; entry++) {
        ZipCentralDirHeader cHeader;
        if (fread(&cHeader, sizeof(ZipCentralDirHeader), 1, fp) != 1) break;
        if (cHeader.signature != 0x02014b50) break;
        
        char *filenameBuf = malloc(cHeader.filenameLength + 1);
        fread(filenameBuf, 1, cHeader.filenameLength, fp);
        filenameBuf[cHeader.filenameLength] = '\0';
        NSString *relPath = [NSString stringWithUTF8String:filenameBuf];
        free(filenameBuf);
        
        // Пропускаем extra & comment
        fseek(fp, cHeader.extraFieldLength + cHeader.commentLength, SEEK_CUR);
        long nextCentralDirOffset = ftell(fp);
        
        if (!relPath) continue;
        
        NSString *destFilePath = [destinationPath stringByAppendingPathComponent:relPath];
        
        // Если это каталог
        if ([relPath hasSuffix:@"/"]) {
            [fm createDirectoryAtPath:destFilePath withIntermediateDirectories:YES attributes:nil error:nil];
            fseek(fp, nextCentralDirOffset, SEEK_SET);
            continue;
        }
        
        // Создаем родительские директории при необходимости
        [fm createDirectoryAtPath:[destFilePath stringByDeletingLastPathComponent]
      withIntermediateDirectories:YES
                       attributes:nil
                            error:nil];
        
        // 3. Чтение локального заголовка
        fseek(fp, cHeader.localHeaderOffset, SEEK_SET);
        ZipLocalHeader lHeader;
        fread(&lHeader, sizeof(ZipLocalHeader), 1, fp);
        if (lHeader.signature != 0x04034b50) {
            fseek(fp, nextCentralDirOffset, SEEK_SET);
            continue;
        }
        
        // Данные начинаются сразу после имени и extra поля в локальном заголовке
        fseek(fp, lHeader.filenameLength + lHeader.extraFieldLength, SEEK_CUR);
        
        FILE *outFile = fopen([destFilePath UTF8String], "wb");
        if (!outFile) {
            fseek(fp, nextCentralDirOffset, SEEK_SET);
            continue;
        }
        
        if (cHeader.compressionMethod == 0) {
            // Без сжатия (STORED)
            uint8_t chunk[4096];
            uint32_t remaining = cHeader.uncompressedSize;
            while (remaining > 0) {
                size_t toRead = remaining > sizeof(chunk) ? sizeof(chunk) : remaining;
                size_t readBytes = fread(chunk, 1, toRead, fp);
                if (readBytes <= 0) break;
                fwrite(chunk, 1, readBytes, outFile);
                remaining -= readBytes;
            }
        } else if (cHeader.compressionMethod == 8) {
            // Сжатие DEFLATE через zlib
            z_stream strm;
            memset(&strm, 0, sizeof(strm));
            // -MAX_WBITS говорит zlib читать "сырой" deflate поток без zlib-заголовка
            if (inflateInit2(&strm, -MAX_WBITS) == Z_OK) {
                uint8_t inBuffer[4096];
                uint8_t outBuffer[4096];
                uint32_t compRemaining = cHeader.compressedSize;
                int ret = Z_OK;
                
                while (compRemaining > 0 && ret != Z_STREAM_END) {
                    size_t toRead = compRemaining > sizeof(inBuffer) ? sizeof(inBuffer) : compRemaining;
                    size_t readBytes = fread(inBuffer, 1, toRead, fp);
                    if (readBytes <= 0) break;
                    compRemaining -= readBytes;
                    
                    strm.avail_in = (uInt)readBytes;
                    strm.next_in = inBuffer;
                    
                    do {
                        strm.avail_out = sizeof(outBuffer);
                        strm.next_out = outBuffer;
                        ret = inflate(&strm, Z_NO_FLUSH);
                        size_t have = sizeof(outBuffer) - strm.avail_out;
                        if (have > 0) {
                            fwrite(outBuffer, 1, have, outFile);
                        }
                    } while (strm.avail_out == 0 && ret != Z_STREAM_END);
                }
                inflateEnd(&strm);
            }
        }
        
        fclose(outFile);
        fseek(fp, nextCentralDirOffset, SEEK_SET);
    }
    
    fclose(fp);
    return YES;
}

@end
