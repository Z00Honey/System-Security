// analysis.c
// x86_64-w64-mingw32-gcc -shared -o ../build/analysis.dll analysis.c "-Wl,--out-implib,libanalysis.a"

#ifdef _WIN32
    #include <windows.h>
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
    #define BOOL int
    #define WINAPI
    #define HINSTANCE void*
    #define DWORD unsigned long
    #define LPVOID void*
    #define TRUE 1
#endif

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include "signature.h"

// 함수 선언
int verify_file_signature(const char *filename, unsigned char *data, size_t file_size, long *footer_end_pos);
int detect_embedded_files(unsigned char *data, size_t data_size, char embedded_extensions[][10], int *count);
char* strdup_s(const char *src);

// Windows DLL 관련 코드를 조건부 컴파일
#ifdef _WIN32
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}
#endif

// 내보낼 함수 선언
DLL_EXPORT int analyze_file(const char* filename, char* result, int result_size) {
    FILE *file = NULL;

#ifdef _WIN32
    // UTF-8 문자열을 Wide 문자열로 변환
    int wide_size = MultiByteToWideChar(CP_UTF8, 0, filename, -1, NULL, 0);
    if (wide_size == 0) {
        snprintf(result, result_size, "파일 이름 변환 실패");
        return 0;
    }

    wchar_t *wfilename = (wchar_t*)malloc(wide_size * sizeof(wchar_t));
    if (!wfilename) {
        snprintf(result, result_size, "메모리 할당 실패");
        return 0;
    }

    MultiByteToWideChar(CP_UTF8, 0, filename, -1, wfilename, wide_size);

    // Wide 문자열을 사용하여 파일 열기
    file = _wfopen(wfilename, L"rb");
    free(wfilename);
#else
    // 비-Windows 환경에서는 기존 방식 사용
    file = fopen(filename, "rb");
#endif

    if (!file) {
        snprintf(result, result_size, "파일 열기 실패");
        return 0;
    }

    // 파일 크기 구하기
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    if (file_size <= 0) {
        snprintf(result, result_size, "파일 크기 확인 실패");
        fclose(file);
        return 0;
    }
    fseek(file, 0, SEEK_SET);

    // 전체 파일 내용을 메모리에 로드
    unsigned char *data = (unsigned char*)malloc(file_size);
    if (!data) {
        snprintf(result, result_size, "메모리 할당 실패");
        fclose(file);
        return 0;
    }

    size_t read_bytes = fread(data, 1, file_size, file);
    fclose(file);
    if (read_bytes != file_size) {
        snprintf(result, result_size, "파일 읽기 실패");
        free(data);
        return 0;
    }

    long footer_end_pos = 0;
    int verify_result = 0;  // 시그니처 검증 결과
    int embedded_count = 0; // 숨겨진 파일 개수
    char embedded_list[100] = ""; // 숨겨진 파일 목록 저장 버퍼

    // 파일 시그니처 및 푸터 검사
    if ((verify_result = verify_file_signature(filename, data, file_size, &footer_end_pos))) {
        printf("파일 시그니처와 푸터가 일치합니다: %s\n", filename);
    } else {
        printf("파일 시그니처 또는 푸터가 일치하지 않습니다: %s\n", filename);
    }

    // 푸터 이후에 숨겨진 파일 시그니처 검사
    if (footer_end_pos < file_size) {
        size_t embedded_size = file_size - footer_end_pos;
        unsigned char *embedded_data = data + footer_end_pos;

        char embedded_extensions[10][10]; // 최대 10개의 숨겨진 파일
        if (detect_embedded_files(embedded_data, embedded_size, embedded_extensions, &embedded_count)) {
            if (embedded_count > 0) {
                printf("푸터 이후에 숨겨진 파일 시그니처가 감지되었습니다 (%d개):\n", embedded_count);
                for (int i = 0; i < embedded_count; i++) {
                    printf(" - %s\n", embedded_extensions[i]);
                    // 숨겨진 파일 목록에 추가
                    if (i > 0) {
                        strncat(embedded_list, ", ", sizeof(embedded_list) - strlen(embedded_list) - 1);
                    }
                    strncat(embedded_list, embedded_extensions[i], sizeof(embedded_list) - strlen(embedded_list) - 1);
                }
            } else {
                printf("푸터 이후에 숨겨진 파일 시그니처가 없습니다.\n");
            }
        } else {
            printf("푸터 이후 파일 시그니처 검사에 실패했습니다.\n");
        }
    } else {
        printf("푸터 이후에 숨겨진 데이터가 없습니다.\n");
    }

    // 이중 확장자 검사
    int double_extension = 0;
    char double_extension_list[100] = "";

    // 파일 이름에서 마지막 점(.) 위치 찾기
    const char *last_dot = strrchr(filename, '.');
    if (last_dot != NULL && last_dot != filename) {
        // 두 번째 마지막 점 찾기
        const char *second_last_dot = NULL;
        for (const char *p = filename; p < last_dot; p++) {
            if (*p == '.') {
                second_last_dot = p;
            }
        }

        if (second_last_dot != NULL && second_last_dot != filename) {
            double_extension = 1;
            // 이중 확장자 목록 구성
            snprintf(double_extension_list, sizeof(double_extension_list), "%s%s",
                     second_last_dot, last_dot);
        }
    }

    // 추가: embedded_count, embedded_list, double_extension, double_extension_list 값을 다시 출력하여 확인
    printf("최종 embedded_count: %d\n", embedded_count);
    printf("최종 embedded_list: %s\n", embedded_list);
    printf("이중 확장자 여부: %s\n", double_extension ? "있음" : "없음");
    if (double_extension) {
        printf("이중 확장자 목록: %s\n", double_extension_list);
    }

    // 결과를 result 버퍼에 저장 (숨겨진 파일 목록 및 이중 확장자 추가)
    if (double_extension) {
        snprintf(result, result_size, "분석 완료: %s\n시그니처 검사: %s\n숨겨진 파일: %d개\n숨겨진 파일 목록: %s\n이중 확장자: 있음\n이중 확장자 목록: %s",
                 filename, 
                 (verify_result ? "일치" : "불일치"),
                 embedded_count,
                 embedded_list,
                 double_extension_list);
    } else {
        snprintf(result, result_size, "분석 완료: %s\n시그니처 검사: %s\n숨겨진 파일: %d개\n숨겨진 파일 목록: %s\n이중 확장자: 없음",
                 filename, 
                 (verify_result ? "일치" : "불일치"),
                 embedded_count,
                 embedded_list);
    }

    free(data);
    return 1;
}

// 안전한 strdup 함수 (메모리 할당 실패 시 NULL 반환)
char* strdup_s(const char *src) {
    if (src == NULL) return NULL;
    size_t len = strlen(src);
    char *dst = (char*)malloc(len + 1);
    if (dst) {
        strcpy(dst, src);
    }
    return dst;
}

// 파일 시그니처 및 푸터 검사 함수
int verify_file_signature(const char *filename, unsigned char *data, size_t file_size, long *footer_end_pos) {
    // 초기화
    *footer_end_pos = 0;

    // 파일 확장자 추출 (마지막 '.' 이후)
    const char *last_dot = strrchr(filename, '.');
    if (!last_dot) {
        // 확장자 없음
        return 0;
    }

    // 찾은 확장자와 일치하는 시그니처 찾기
    FileSignature *sig = NULL;
    for (int i = 0; i < SIGNATURE_COUNT; i++) {
        if (signatures[i].extension == NULL) continue; // 안전하게
        if (strcasecmp(last_dot, signatures[i].extension) == 0) {
            sig = &signatures[i];
            break;
        }
    }

    if (!sig) {
        // 지원하지 않는 확장자
        return 0;
    }

    // 헤더 검사
    size_t max_header_size = 0;
    for (size_t i = 0; i < sig->header_count; i++) {
        if (sig->header_sizes[i] > max_header_size) {
            max_header_size = sig->header_sizes[i];
        }
    }

    if (max_header_size > file_size) {
        // 파일 크기가 헤더보다 작음
        return 0;
    }

    int header_match = 0;
    for (size_t i = 0; i < sig->header_count; i++) {
        if (sig->header_sizes[i] > file_size) continue;
        if (memcmp(data, sig->headers[i], sig->header_sizes[i]) == 0) {
            header_match = 1;
            break;
        }
    }

    if (!header_match) {
        // 헤더 불일치
        return 0;
    }

    // 푸터 검사 (푸터가 정의된 경우)
    if (sig->footer_count > 0) {
        // 푸터는 파일의 끝에서부터 검사
        for (size_t i = 0; i < sig->footer_count; i++) {
            size_t footer_size = sig->footer_sizes[i];
            if (footer_size > file_size) continue;
            unsigned char *footer_pos = data + file_size - footer_size;
            if (memcmp(footer_pos, sig->footers[i], footer_size) == 0) {
                // 푸터 일치
                *footer_end_pos = file_size;
                return 1;
            }
        }
        // 푸터가 일치하지 않음
        return 0;
    } else {
        // 푸터가 정의되지 않은 경우, 푸터 이후 데이터 없음
        *footer_end_pos = file_size;
        return 1;
    }
}

// 내부 파일 시그니처 탐지 함수
int detect_embedded_files(unsigned char *data, size_t data_size, char embedded_extensions[][10], int *count) {
    *count = 0;

    // 각 파일 시그니처를 검색
    for (int i = 0; i < SIGNATURE_COUNT; i++) {
        if (signatures[i].extension == NULL) continue; // 안전하게
        FileSignature *sig = &signatures[i];
        for (size_t h = 0; h < sig->header_count; h++) {
            unsigned char *header = sig->headers[h];
            size_t header_size = sig->header_sizes[h];

            // 검색 시작
            unsigned char *pos = data;
            while ((pos = memchr(pos, header[0], data + data_size - pos)) != NULL) {
                // 가능한 시그니처 위치 확인
                if ((size_t)(data + data_size - pos) >= header_size &&
                    memcmp(pos, header, header_size) == 0) {
                    // 이미 감지된 확장자인지 확인
                    int already_detected = 0;
                    for (int e = 0; e < *count; e++) {
                        if (strcasecmp(embedded_extensions[e], sig->extension) == 0) {
                            already_detected = 1;
                            break;
                        }
                    }
                    if (!already_detected && *count < 10) { // 최대 10개
                        strncpy(embedded_extensions[*count], sig->extension, 9);
                        embedded_extensions[*count][9] = '\0'; // Null-terminate
                        (*count)++;
                    }
                }
                pos += 1; // 다음 검색 시작 위치
            }
        }
    }

    return 1;
}
