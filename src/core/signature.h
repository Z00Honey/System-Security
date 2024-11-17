// signature.h
#ifndef SIGNATURE_H
#define SIGNATURE_H

#include <stddef.h>

// 최대 시그니처 개수 정의 (실제 초기화된 시그니처 수에 맞게 설정)
#define SIGNATURE_COUNT 50

// 파일 시그니처 구조체
typedef struct {
    char *extension;                      // 파일 확장자
    unsigned char headers[10][16];        // 가능한 헤더들 (최대 10개)
    size_t header_sizes[10];              // 각 헤더의 크기
    size_t header_count;                  // 헤더 개수
    unsigned char footers[10][16];        // 가능한 푸터들 (최대 10개)
    size_t footer_sizes[10];              // 각 푸터의 크기
    size_t footer_count;                  // 푸터 개수
} FileSignature;

// 지원하는 파일 시그니처 목록
FileSignature signatures[SIGNATURE_COUNT] = {
    // JPEG (.jpg, .jpeg)
    {
        ".jpg",
        {
            {0xFF, 0xD8, 0xFF}
        },
        {3},
        1,
        {
            {0xFF, 0xD9}
        },
        {2},
        1
    },
    // JPEG2000 (.jp2)
    {
        ".jp2",
        {
            {0x00, 0x00, 0x00, 0x0C, 0x6A, 0x50, 0x20, 0x20, 0x0D, 0x0A, 0x87, 0x0A}
        },
        {12},
        1,
        { },
        {0},
        0
    },
    // PNG (.png)
    {
        ".png",
        {
            {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}
        },
        {8},
        1,
        {
            {0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82}
        },
        {8},
        1
    },
    // GIF (.gif)
    {
        ".gif",
        {
            {0x47, 0x49, 0x46, 0x38, 0x37, 0x61}, // GIF87a
            {0x47, 0x49, 0x46, 0x38, 0x39, 0x61}  // GIF89a
        },
        {6, 6},
        2,
        {
            {0x3B}
        },
        {1},
        1
    },
    // BMP (.bmp)
    {
        ".bmp",
        {
            {0x42, 0x4D}
        },
        {2},
        1,
        { },
        {0},
        0
    },
    // PDF (.pdf)
    {
        ".pdf",
        {
            {0x25, 0x50, 0x44, 0x46, 0x2D} // %PDF-
        },
        {5},
        1,
        {
            {0x25, 0x25, 0x45, 0x4F, 0x46} // %%EOF
        },
        {5},
        1
    },
    // ZIP (.zip)
    {
        ".zip",
        {
            {0x50, 0x4B, 0x03, 0x04},
            {0x50, 0x4B, 0x05, 0x06},
            {0x50, 0x4B, 0x07, 0x08}
        },
        {4, 4, 4},
        3,
        { },
        {0},
        0
    },
    // RAR (.rar)
    {
        ".rar",
        {
            {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x00}, // Rar v1.5
            {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x01, 0x00} // Rar v5.0
        },
        {7, 8},
        2,
        { },
        {0},
        0
    },
    // 7z (.7z)
    {
        ".7z",
        {
            {0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C}
        },
        {6},
        1,
        { },
        {0},
        0
    },
    // GZIP (.gz)
    {
        ".gz",
        {
            {0x1F, 0x8B, 0x08}
        },
        {3},
        1,
        { },
        {0},
        0
    },
    // ELF (.elf)
    {
        ".elf",
        {
            {0x7F, 0x45, 0x4C, 0x46}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // EXE (.exe)
    {
        ".exe",
        {
            {0x4D, 0x5A} // MZ
        },
        {2},
        1,
        { },
        {0},
        0
    },
    // DLL (.dll)
    {
        ".dll",
        {
            {0x4D, 0x5A} // MZ (same as EXE)
        },
        {2},
        1,
        { },
        {0},
        0
    },
    // MSI (.msi)
    {
        ".msi",
        {
            {0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1} // OLE Compound File
        },
        {8},
        1,
        { },
        {0},
        0
    },
    // MP4 (.mp4)
    {
        ".mp4",
        {
            {0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, 0x4D, 0x50, 0x34, 0x32},
            {0x00, 0x00, 0x00, 0x1C, 0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6F, 0x6D}
        },
        {12, 12},
        2,
        { },
        {0},
        0
    },
    // DOCX (.docx)
    {
        ".docx",
        {
            {0x50, 0x4B, 0x03, 0x04}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // XLSX (.xlsx)
    {
        ".xlsx",
        {
            {0x50, 0x4B, 0x03, 0x04}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // PPTX (.pptx)
    {
        ".pptx",
        {
            {0x50, 0x4B, 0x03, 0x04}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // APK (.apk)
    {
        ".apk",
        {
            {0x50, 0x4B, 0x03, 0x04}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // ISO (.iso)
    {
        ".iso",
        {
            {0x43, 0x44, 0x30, 0x30, 0x31} // CD001
        },
        {5},
        1,
        { },
        {0},
        0
    },
    // FLAC (.flac)
    {
        ".flac",
        {
            {0x66, 0x4C, 0x61, 0x43}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // WAV (.wav)
    {
        ".wav",
        {
            {0x52, 0x49, 0x46, 0x46}
        },
        {4},
        1,
        {
            {0x57, 0x41, 0x56, 0x45} // WAVE
        },
        {4},
        1
    },
    // AVI (.avi)
    {
        ".avi",
        {
            {0x52, 0x49, 0x46, 0x46}
        },
        {4},
        1,
        {
            {0x41, 0x56, 0x49, 0x20} // 'AVI '
        },
        {4},
        1
    },
    // MOV (.mov)
    {
        ".mov",
        {
            {0x00, 0x00, 0x00, 0x14, 0x66, 0x74, 0x79, 0x70, 0x71, 0x74, 0x20, 0x20}
        },
        {12},
        1,
        { },
        {0},
        0
    },
    // MKV (.mkv)
    {
        ".mkv",
        {
            {0x1A, 0x45, 0xDF, 0xA3}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // TAR.GZ (.tgz)
    {
        ".tgz",
        {
            {0x1F, 0x8B, 0x08}
        },
        {3},
        1,
        { },
        {0},
        0
    },
    // JSON (.json)
    {
        ".json",
        {
            {0x7B, 0x22, 0x7D}, // {"}
            {0x5B, 0x22, 0x5D}  // ["
        },
        {3, 3},
        2,
        { },
        {0},
        0
    },
    // XML (.xml)
    {
        ".xml",
        {
            {0x3C, 0x3F, 0x78, 0x6D, 0x6C, 0x20}
        },
        {6},
        1,
        { },
        {0},
        0
    },
    // SQLite (.sqlite)
    {
        ".sqlite",
        {
            {0x53, 0x51, 0x4C, 0x69, 0x74, 0x65, 0x20, 0x66, 0x6F, 0x72, 0x6D, 0x61, 0x74, 0x20, 0x33, 0x00}
        },
        {16},
        1,
        { },
        {0},
        0
    },
    // PHP (.php)
    {
        ".php",
        {
            {0x3C, 0x3F, 0x50, 0x48, 0x50}
        },
        {5},
        1,
        { },
        {0},
        0
    },
    // Python (.py)
    {
        ".py",
        {
            {0x23, 0x21, 0x2F, 0x75, 0x73, 0x72, 0x2F, 0x62, 0x69, 0x6E, 0x2F, 0x70, 0x79}
        },
        {13},
        1,
        { },
        {0},
        0
    },
    // Shell Script (.sh)
    {
        ".sh",
        {
            {0x23, 0x21, 0x2F, 0x62, 0x69, 0x6E, 0x2F, 0x73, 0x68}
        },
        {9},
        1,
        { },
        {0},
        0
    },
    // Ruby (.rb)
    {
        ".rb",
        {
            {0x23, 0x21, 0x2F, 0x75, 0x73, 0x72, 0x2F, 0x62, 0x69, 0x6E, 0x2F, 0x72, 0x75, 0x62, 0x79}
        },
        {15},
        1,
        { },
        {0},
        0
    },
    // Perl (.pl)
    {
        ".pl",
        {
            {0x23, 0x21, 0x2F, 0x75, 0x73, 0x72, 0x2F, 0x62, 0x69, 0x6E, 0x2F, 0x70, 0x65, 0x72, 0x6C}
        },
        {15},
        1,
        { },
        {0},
        0
    },
    // Swift (.swift)
    {
        ".swift",
        {
            {0x73, 0x77, 0x69, 0x66, 0x74}
        },
        {5},
        1,
        { },
        {0},
        0
    },
    // Java (.class)
    {
        ".class",
        {
            {0xCA, 0xFE, 0xBA, 0xBE}
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // Scala (.scala)
    {
        ".scala",
        {
            {0x2F, 0x2F, 0x2F, 0x2F} // Assumed comment start
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // C# (.cs)
    {
        ".cs",
        {
            {0x2F, 0x2A, 0x2A, 0x2A} // /* */
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // C++ (.cpp)
    {
        ".cpp",
        {
            {0x2F, 0x2A, 0x2A, 0x2A} // /* */
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // C (.c)
    {
        ".c",
        {
            {0x2F, 0x2A, 0x2A, 0x2A} // /* */
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // HTML (.html)
    {
        ".html",
        {
            {0x3C, 0x21, 0x44, 0x4F, 0x43, 0x54, 0x59, 0x50, 0x45, 0x20, 0x68, 0x74, 0x6D, 0x6C}
        },
        {14},
        1,
        { },
        {0},
        0
    },
    // CSS (.css)
    {
        ".css",
        {
            {0x2F, 0x2A, 0x2A, 0x2A} // /* */
        },
        {4},
        1,
        { },
        {0},
        0
    },
    // Lua (.lua)
    {
        ".lua",
        {
            {0x2D, 0x2D, 0x20} // --
        },
        {3},
        1,
        { },
        {0},
        0
    },
    // Haskell (.hs)
    {
        ".hs",
        {
            {0x2D, 0x2D, 0x20} // --
        },
        {3},
        1,
        { },
        {0},
        0
    },
    // Rust (.rs)
    {
        ".rs",
        {
            {0x3F, 0x21, 0x72, 0x75, 0x73, 0x74}
        },
        {6},
        1,
        { },
        {0},
        0
    },
    // 추가 파일 시그니처를 여기에 추가
};

#endif // SIGNATURE_H
